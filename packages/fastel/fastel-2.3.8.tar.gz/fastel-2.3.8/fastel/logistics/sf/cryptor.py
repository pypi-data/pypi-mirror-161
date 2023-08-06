import base64
import hashlib
import json
import random
import socket
import string
import struct
import time
from typing import Any, Dict, Optional, Tuple

from Crypto.Cipher import AES

from fastel.exceptions import APIException
from fastel.logistics.sf import ierror


class SHA1:
    """计算消息签名接口"""

    def getSHA1(
        self, token: str, timestamp: str, nonce: str, encrypt: str
    ) -> Tuple[int, Optional[str]]:
        """用SHA1算法生成安全签名
        @param token:  access token
        @param timestamp: 时间戳
        @param encrypt: 密文
        @param nonce: 随机字符串
        @return: 安全签名
        """
        try:
            sortlist = [token, timestamp, nonce, encrypt]
            sortlist.sort()
            sha = hashlib.sha1()
            sha.update("".join(sortlist).encode())
            return ierror.WXBizMsgCrypt_OK, sha.hexdigest()
        except (RuntimeError):
            # print e
            return ierror.WXBizMsgCrypt_ComputeSignature_Error, None

    def getSHA2(
        self, token: str, timestamp: str, nonce: str, encrypt: str
    ) -> Tuple[int, Optional[str]]:
        """用SHA256算法生成安全签名
        @param token:  access token
        @param timestamp: 时间戳
        @param encrypt: 密文
        @param nonce: 随机字符串
        @return: 安全签名
        """
        try:
            sortlist = [token, timestamp, nonce, encrypt]
            sortlist.sort()
            sha = hashlib.sha256()
            # print("shaStr:"+"".join(sortlist))
            sha.update(("".join(sortlist)).encode())
            return ierror.WXBizMsgCrypt_OK, sha.hexdigest()
        except (RuntimeError):
            # print e
            return ierror.WXBizMsgCrypt_ComputeSignature_Error, None


class PKCS7Encoder:
    """提供基于PKCS7算法的加解密接口"""

    block_size = 32

    def encode(self, text: bytes) -> bytes:
        """对需要加密的明文进行填充补位
        @param text: 需要进行填充补位操作的明文
        @return: 补齐明文字符串
        """
        text_length = len(text)
        # 计算需要填充的位数
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        # 获得补位所用的字符
        pad = chr(amount_to_pad)
        return text + str.encode(pad * amount_to_pad)

    def decode(self, decrypted: bytes) -> bytes:
        """删除解密后明文的补位字符
        @param decrypted: 解密后的明文
        @return: 删除补位字符后的明文
        """
        pad = decrypted[-1]
        # print("pad:"+str(pad))
        if pad < 1 or pad > 32:
            pad = 0
        return decrypted[:-pad]


class Prpcrypt:
    """提供接收和推送给公众平台消息的加解密接口"""

    def __init__(self, key: bytes) -> None:
        # self.key = base64.b64decode(key+"=")
        self.key = key
        # 设置加解密模式为AES的CBC模式
        self.mode = AES.MODE_CBC

    def encrypt(self, text: str, appKey: str) -> Tuple[int, Optional[str]]:
        """对明文进行加密
        @param text: 需要加密的明文
        @return: 加密得到的字符串
        """
        # 16位随机字符串添加到明文开头
        textBytes = (
            str.encode(self.get_random_str())
            + struct.pack("I", socket.htonl(len(text.encode())))
            + str.encode(text)
            + str.encode(appKey)
        )
        # print("需要加密的明文:"+text)
        # 使用自定义的填充方式对明文进行补位填充
        pkcs7 = PKCS7Encoder()
        textBytes = pkcs7.encode(textBytes)
        # print("补位:"+text)
        # 加密
        cryptor = AES.new(self.key, self.mode, self.key[:16])
        try:
            ciphertext = cryptor.encrypt(textBytes)
            # 使用BASE64对加密后的字符串进行编码
            # print("密文:"+bytes.decode(base64.b64encode(ciphertext)))
            return ierror.WXBizMsgCrypt_OK, bytes.decode(base64.b64encode(ciphertext))
        except (RuntimeError):
            # print e
            return ierror.WXBizMsgCrypt_EncryptAES_Error, None

    def decrypt(self, text: str, appKey: str) -> Tuple[int, Optional[str]]:
        """对解密后的明文进行补位删除
        @param text: 密文
        @return: 删除填充补位后的明文
        """
        try:
            cryptor = AES.new(self.key, self.mode, self.key[:16])
            # 使用BASE64对密文进行解码，然后AES-CBC解密
            plain_text = cryptor.decrypt(base64.b64decode(text))
            # print("解密:"+bytes.decode(plain_text))
        except (RuntimeError):
            # print e
            return ierror.WXBizMsgCrypt_DecryptAES_Error, None
        try:
            # 去掉补位字符串
            pkcs7 = PKCS7Encoder()
            content = pkcs7.decode(plain_text)
            # print("随机字符串:"+str(content))
            # print("struct.unpack:"+str(struct.unpack("I",content[16: 20])))
            xml_len = socket.ntohl(struct.unpack("I", content[16:20])[0])
            # print("xml_len:"+str(xml_len))
            xml_content = bytes.decode(content[20 : xml_len + 20])
            # print("xml_content:"+xml_content)
            from_appKey = bytes.decode(content[xml_len + 20 :])
            # print("from_appKey:"+from_appKey)
        except (RuntimeError):
            # print e
            return ierror.WXBizMsgCrypt_IllegalBuffer, None
        if from_appKey != appKey:
            return ierror.WXBizMsgCrypt_ValidateAppKey_Error, None
        # print("明文:"+str(xml_content))
        return 0, xml_content

    def get_random_str(self) -> str:
        """随机生成16位字符串
        @return: 16位字符串
        """
        rule = string.ascii_letters + string.digits
        str = random.sample(rule, 16)
        return "".join(str)


class SFCryptor:
    # 构造函数
    # @param access token: 接口获取的token
    # @param aes_key: 应用上的EncodingAESKey
    # @param app_key: 应用的AppKey
    def __init__(
        self, aes_key: str, app_key: str, access_token: Optional[str] = None
    ) -> None:
        try:
            self.key = base64.b64decode(aes_key + "=")
            assert len(self.key) == 32
        except Exception:
            raise APIException(
                status_code=400,
                error="AES_Encoding_error",
                detail="SF EncodingAESKey unvalid !",
            )
        self.token = access_token
        self.app_key = app_key

    def encrypt_msg(
        self, msg: str, nonce: str, timestamp: Optional[str]
    ) -> Tuple[int, Optional[str], Optional[str]]:
        # 将公众号回复用户的消息加密打包
        # @param msg: 需加密的报文
        # @param timestamp: 时间戳，可以自己生成,如为None则自动用当前时间
        # @param nonce: 随机串，可以自己生成
        # encrypt_msg: 加密后的可以直接回复用户的密文，包括msg_signature, timestamp, nonce, encrypt的xml格式的字符串,
        # return：成功0，encrypt_msg,失败返回对应的错误码None
        if not self.token:
            raise APIException(
                status_code=400, error="SF_Encrypt_Token_not_found", detail=""
            )
        pc = Prpcrypt(self.key)
        ret, encrypt = pc.encrypt(msg, self.app_key)
        if not encrypt or ret != 0:
            return ret, encrypt, None
        if timestamp is None:
            timestamp = str(int(time.time()))
        # 生成安全签名
        sha1 = SHA1()
        ret, signature = sha1.getSHA2(self.token, timestamp, nonce, encrypt)
        if not signature or ret != 0:
            return ret, None, signature
        # print("密文："+encrypt+",签名:"+signature)
        return ret, encrypt, signature

    def decrypt_msg(self, post_data: str) -> Tuple[int, Dict[str, Any]]:
        # 获取解密后的明文
        # @param post_data: 密文
        #  xml_content: 解密后的原文，当return返回0时有效
        # @return: 成功0，失败返回对应的错误码
        # 验证安全签名
        pc = Prpcrypt(self.key)
        ret, decrypt_data = pc.decrypt(post_data, self.app_key)
        if decrypt_data:
            result = json.loads(decrypt_data)
            assert isinstance(result, dict)
            return ret, result
        else:
            return ret, {"ERROR": "json error"}

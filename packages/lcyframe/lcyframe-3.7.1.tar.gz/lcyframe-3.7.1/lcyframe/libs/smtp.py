#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re, os, logging, traceback
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from email.utils import formataddr


class SmtpServer(object):
    def __init__(self, **kwargs):
        debuglevel = kwargs.pop("debuglevel", False)
        smtp_ssl = kwargs.get("smtp_ssl", True)
        keyfile = kwargs.pop("keyfile", None)
        certfile = kwargs.pop("keyfile", None)
        source_address = kwargs.pop("source_address", None)
        timeout = kwargs.pop("timeout", None)
        local_hostname = kwargs.pop("local_hostname", None)
        context = kwargs.pop("context", None)

        self.smtp_host = kwargs["smtp_host"]
        self.smtp_post = kwargs["smtp_post"]  # SMTP端口25, SMTP_SSL安全连接端口号465或587
        self.smtp_ssl = kwargs.get("smtp_ssl", True)  # 是否使用ssl
        self.username = kwargs.get("username", "")  # 登录SMTP服务器的账号
        self.password = kwargs.get("password", "")  # SMTP客户端授权密码
        self.smtp_email = kwargs.get("smtp_email", "")  # "发件人的昵称<123220663@qq.com>"

        if smtp_ssl:
            connection_class = smtplib.SMTP_SSL(self.smtp_host, self.smtp_post, local_hostname, keyfile, certfile,
                                                timeout, source_address, context)
        else:
            connection_class = smtplib.SMTP(self.smtp_host, self.smtp_post, local_hostname, timeout, source_address)

        self.smtp = connection_class
        if debuglevel:
            self.smtp.set_debuglevel(True)  # debug模式打印详情

    def connection(self):
        self.smtp.connect(self.smtp_host, self.smtp_post)
        self.smtp.login(self.username, self.password)

    def send(self, to_emails: [str, list, tuple],
             title, message="", html_message=None,
             images=None, attachs=None, from_email=None):
        """
        from_email: yourself email
        to_mails:"one@one.org" or ["one@one.org","two@two.org","three@three.org","four@four.org"]
        message: 文本内容
        html_message: html内容，注意邮件的 HTML 文本中一般邮件服务商添加外链是无效的
                <p>邮件文本内容</p>
                <p><a href="http://www.xxx.com">链接</a></p>
                <p>内容中的图片未被显示时，需添加发件人信任。或者点击邮件页面中的"显示图片 信任此发件人的图片"</p>
                <p><img src="http://www.url.com/x.png"></p>
                <p>图片标签：以下需添加image1的标签图片</p>
                <p><img src="cid:image1"></p>

        images: 需要在html_message中出现的图片，
        [path1, path2] or [image_buffer1, image_buffer2]，
        用免费的腾讯邮箱发送，img标签不能正常显示

        推荐在html_message使用完整的图片地址实现

        attachs: 附件地址或者文件数据列表
        [path1, path2] or [buffer1, buffer2]
        """
        mime_message = MIMEMultipart("related")
        # mime_message = MIMEText(message, 'plain', 'utf-8')

        # mime_message['From'] = Header(from_email, 'utf-8')  # 发送者
        # mime_message['To'] = Header(",".join(to_emails), 'utf-8')  # 接收者
        # mime_message['To'] = formataddr(("指定收件人昵称", ",".join(to_emails)))

        from_email = from_email or self.smtp_email
        # 标题
        mime_message['Subject'] = Header(title, 'utf-8')
        # 发件人
        if re.search(r'<.+>', from_email):
            smtp_name, from_email = from_email.split("<")
        else:
            smtp_name, from_email = from_email, from_email
        mime_message['From'] = formataddr((smtp_name.rstrip(" "), from_email.rstrip(">")))
        # 收件人
        to_emails = [to_emails] if not isinstance(to_emails, (list, tuple)) else to_emails
        for email in to_emails:
            mime_message.add_header("to", email)  # 接收者

        # 文本
        if message:
            mime_message.attach(MIMEText(message, 'plain', 'utf-8'))

        # html
        if html_message:
            mime_html = MIMEMultipart("alternative")
            mime_message.attach(mime_html)
            mime_html.attach(MIMEText(html_message, 'html', 'utf-8'))

            # 图片: 需提供html_message内容,并预留image为前缀的名称标签
            if images:
                images = [images] if not isinstance(images, (list, tuple)) else images
                for i, image in enumerate(images):
                    if os.path.isfile(image):
                        with open(image, 'rb') as p:
                            data = p.read()
                    else:
                        data = image
                    mime_image = MIMEImage(data)
                    # 定义图片 ID，在 HTML 文本中引用
                    mime_image.add_header('Content-ID', 'image%s' % (i + 1))
                    mime_message.attach(mime_image)
        # 附件
        if attachs:
            attachs = [attachs] if not isinstance(attachs, (list, tuple)) else attachs
            for attach in attachs:
                if os.path.isfile(attach):
                    with open(attach, 'rb') as p:
                        data = p.read()
                else:
                    data = attach
                mime_attach = MIMEText(data, 'base64', 'utf-8')
                mime_attach["Content-Type"] = 'application/octet-stream'
                mime_attach["Content-Disposition"] = 'attachment; filename="%s"' % os.path.basename(attach)
                mime_message.attach(mime_attach)

        self.connection()
        result = self.smtp.sendmail(from_email, to_emails, mime_message.as_string())
        self.smtp.quit()
        return result

    def send_email(self, to_emails: [str, list, tuple],
                   title, message="", html_message=None,
                   images=None, attachs=None, from_email=None):
        try:
            result = self.send(to_emails,
                               title, message, html_message,
                               images, attachs, from_email)
        except Exception as e:
            logging.error(traceback.format_exc())
            result = False
        else:
            to_emails = [to_emails] if not isinstance(to_emails, (list, tuple)) else to_emails
            logging.debug("邮件发送成功:%s" % ",".join(to_emails))
            result = result or True
        finally:
            return result


if __name__ == "__main__":
    # SMTP服务器地址
    smtp_host = "smtp.qq.com"
    # SMTP服务端口
    smtp_post = 465  # SMTP端口25, SMTP_SSL安全连接端口号465或587
    # 是否使用ssl
    smtp_ssl = True
    # 登录SMTP服务器的账号
    username = "123220663@qq.com"
    # SMTP客户端授权密码
    password = "ujzrzohozvcybggd"
    # 发件人邮箱
    smtp_email = "发件人的昵称<123220663@qq.com>"

    cli = SmtpServer(smtp_host=smtp_host,
                     smtp_post=smtp_post,
                     smtp_ssl=smtp_ssl,
                     debuglevel=False,
                     smtp_email=smtp_email,
                     username=username,
                     password=password
                     )
    cli.send_email(
        # ["取名字不难<452809783@qq.com>", "昏昏暗暗<123220663@qq.com>"],
        ["452809783@qq.com", "123220663@qq.com"],
        "邮件标题6",
        message="文本",
        html_message="""
        <p style="color:red">邮件文本内容</p>
        <p><a href="http://www.xxx.com">链接</a></p>
        <p>内容中的图片未被显示时，需添加发件人信任。或者点击邮件页面中的"显示图片 信任此发件人的图片"</p>
        <p><img src="https://www.runoob.com/wp-content/uploads/2016/04/smtp4.jpg"></p>
        <p>图片标签：以下需添加image1的标签图片</p>
        <p><img src="cid:image1"></p>
        <p>2222</p>
        """,
        images=["/Users/apple/Downloads/WX20220714-160954@2x.png"],
        attachs=["/Users/apple/Downloads/WX20220714-154222@2x.png"]
    )

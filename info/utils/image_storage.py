from qiniu import Auth, put_file, etag, put_data
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key

access_key = 'uGO5Q_IigT0IXEq-tb65sANUcfHKiI2PHDzOo2-w'
secret_key = 'KXJAsBvyN7eKyI_c8kmSWKP064HXtktDTjzWB0gd'


def image_storage(image_data):
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'information15'
    # 上传到七牛后保存的文件名W
    # key = 'my-python-logo.png'
    key = None
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    # 要上传文件的本地路径
    # localfile = './sync/bbb.jpg'
    # ret, info = put_file(token, key, localfile)
    ret, info = put_data(token, key, image_data)
    # print(info)

    if info.status_code == 200:
        return ret.get("key")
    else:
        return ""


if __name__ == "__main__":
    with open("./11.jpg","rb") as f:
        image_name = image_storage(f.read())
        print(image_name)
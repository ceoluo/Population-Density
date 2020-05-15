import os

project_dir = os.path.dirname(os.path.abspath(__file__))

base_url = "http://127.0.0.1:5000"

# 发送新增人脸信息
post_face_url = base_url + "/recognize/save_face"

# 发送当前现场图片
post_scene_url = base_url + "/recognize/save_scene"

# 检测终端所在地点的类型(0:公交, 1:公交站)
type_code = 0

# 检测地域的id
area_id = 2
# area_id = 4
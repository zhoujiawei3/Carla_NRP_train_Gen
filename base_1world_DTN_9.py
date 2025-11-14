import time
import quaternion

import carla
import random
import os
import numpy as np
import queue
import math
from PIL import Image, ImageDraw
from carla import Vector3D
import cv2
import argparse
import sys
count_transfrom=0
count_weather=0
count_img=-1
const_z=0.812
count_img_empty=-2
camera_transform=None
veh_transform=None

veh_trans_list_global=[]
world_map=None
world_waypointlist=None
parser = argparse.ArgumentParser()
parser.add_argument('--color', type=str, default='255,255,255', help='color name')
parser.add_argument('--output_dir', type=str, default='C:/outputs/DTN/', help='output directory path')
parser.add_argument('--vehicle', type=str, default='vehicle.tesla.model3', help='carla vehicle blueprint id, e.g. vehicle.tesla.model3')
opt = parser.parse_args()
color_name=opt.color
output_dir=opt.output_dir
vehicle_model = opt.vehicle
random.seed(1)

#这个函数是为了找到图像中的红色原点，来调整const_z,因为车辆的中心点在地面上，而想要实现的中心点在车辆中间，在车辆的中心点上方一点点
def draw_red_origin(file_path):
    # 打开图像文件
    image = Image.open(file_path)

    # 获取图像的宽度和高度
    width, height = image.size

    # 创建一个新的图像对象，用于绘制点
    new_image = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(new_image)

    # 计算中心点坐标
    center_x = width // 2
    center_y = height // 2

    # 绘制红色的原点（半径为3个像素）
    radius = 1
    draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), fill=(255, 0, 0))

    # 合并原始图像和绘制的点
    print(new_image.size,image.convert('RGBA').size)
    result_image = Image.alpha_composite(image.convert('RGBA'), new_image)

    # 保存结果图像
    result_file_path = file_path
    result_image.save(result_file_path)

    return result_file_path

def generate_mask(file_path):
    # 打开图像文件
    image = Image.open(file_path)
    pixels=image.load()

    for i in range(image.width):
        for j in range(image.height):
            if pixels[i,j] == (0,0,142,255):
                pixels[i,j] = (255,255,255,255)
            else:

                pixels[i, j] = (0, 0, 0,255)

    # 保存结果图像
    result_file_path = file_path
    image.save(result_file_path)

    return result_file_path
def update_weather_parameters(world):
    # 选择要随机更改的参数
    # parameters_to_update = ['fog_density', 'sun_altitude_angle']
    #
    # # 在范围内生成随机值
    # fog_density_values = [0.0, 25.0, 50.0, 90]
    # sun_altitude_angle = [-90, -30, 30, 90]
    #
    # # 遍历参数列表并随机更改值
    # global count_weather
    #
    # fog_density = fog_density_values[(count_weather) % 4]
    # sun_altitude = sun_altitude_angle[(count_weather // 4) % 4]
    # # weather = world.get_weather()
    # #
    # # if sun_altitude == -90 or sun_altitude == -30:
    # #     weather.fog_density = fog_density
    # #     weather.sun_altitude_angle = sun_altitude
    # #     weather.fog_falloff = 4
    # #
    # #
    # #
    # # else:
    # #     weather.fog_density = fog_density
    # #     weather.sun_altitude_angle = sun_altitude
    # #     weather.fog_falloff = 0.1
    # weather = None
    # if sun_altitude == -90 or sun_altitude == -30:
    #     weather = carla.WeatherParameters(fog_density=fog_density,
    #                                       sun_altitude_angle=sun_altitude,
    #                                       fog_falloff=4)
    # else:
    #     weather = carla.WeatherParameters(fog_density=fog_density,
    #                                       sun_altitude_angle=sun_altitude,
    #                                       fog_falloff=4)
    # print(f"weather change to fog_density: {fog_density}, sun_altitude_angle: {sun_altitude}")
    #
    # count_weather += 1
    # world.set_weather(weather)
    # print(world.get_weather())
    parameters_to_update = ['fog_density', 'sun_altitude_angle']

    # 在范围内生成随机值
    fog_density_values = [0.0, 25.0, 50.0, 90]
    sun_altitude_angle = [-90, -30, 30, 90]

    # 遍历参数列表并随机更改值
    global count_weather

    fog_density = fog_density_values[(count_weather) % 4]
    sun_altitude = sun_altitude_angle[(count_weather // 4) % 4]
    # weather = world.get_weather()
    #
    # if sun_altitude == -90 or sun_altitude == -30:
    #     weather.fog_density = fog_density
    #     weather.sun_altitude_angle = sun_altitude
    #     weather.fog_falloff=4
    #
    #
    # else:
    #     weather.fog_density = fog_density
    #     weather.sun_altitude_angle = sun_altitude
    #     weather.fog_falloff = 4
    weather = None
    if sun_altitude == -90 or sun_altitude == -30:
        weather = carla.WeatherParameters(fog_density=fog_density,
                                          sun_altitude_angle=sun_altitude,
                                          fog_falloff=4)
    else:
        weather = carla.WeatherParameters(fog_density=fog_density,
                                          sun_altitude_angle=sun_altitude,
                                          fog_falloff=0)
    print(f"weather change to fog_density: {fog_density}, sun_altitude_angle: {sun_altitude}")

    count_weather += 1
    world.set_weather(weather)
    print(world.get_weather())

#计算相机的position
def compute_xyz(eulerAngle,forwardVector,length):
    # pitch_radians=math.radians(pitch)
    # yaw_radians = math.radians(yaw)
    # tan_yaw=math.tan(yaw_radians)
    # tan_pitch=math.tan(pitch_radians)
    # cos_yaw=math.cos(yaw_radians)
    # sin_yaw=math.sin(yaw_radians)
    # if yaw!=90 and yaw!=270:
    #     x=math.copysign(1,cos_yaw)*(length**2/(1+tan_yaw**2+tan_pitch**2))**0.5*-1
    #     y=abs(x*tan_yaw)*math.copysign(1,sin_yaw)*-1
    #     z=abs(x*tan_pitch)
    # else:
    #     x=0
    #     z=abs(length*math.sin(pitch_radians))
    #     y=abs(length*math.cos(pitch_radians))*math.copysign(1,sin_yaw)*-1
    # return x,y,z
    pitch=math.radians(eulerAngle.x)
    yaw=math.radians(eulerAngle.y)
    roll=math.radians(eulerAngle.z)
    #direction=(quaternion.Euler(eulerAngle) * Vector3D.forward).normalized
    dirction_x=math.cos(pitch)*math.cos(yaw)
    dirction_y=math.cos(pitch)*math.sin(yaw)
    dirction_z=math.sin(pitch)
    x=-dirction_x*length
    y=-dirction_y*length
    z=-dirction_z*length
    return x,y,z
def sensor_callback_empty(camera_empty,image, sensor_queue, sensor_name):
    global count_img_empty
    global camera_transform
    if 'camera' in sensor_name:
        camera_empty.set_transform(camera_transform)
        image.convert(carla.ColorConverter.CityScapesPalette)
        # i = np.array(image.raw_data)
        # i2 = i.reshape((IM_HEIIGHT, IM_WIDTH, 4))
        # i3 = i2[:, :, : 3]
        new_emp_img_filename = "data" + str(count_img_empty + 2) + ".png"
        image.save_to_disk(os.path.join('../outputs/DTN/masks', new_emp_img_filename))
        #generate_mask(os.path.join('../outputs/mask', '%06d.png' % (count_img_empty+1)))
    count_img_empty+=1
    # sensor_queue.put((image.frame, sensor_name))
    sensor_queue.put((sensor_name))


def sensor_callback(world,camera,ego_vehicle,spectator,sensor_data, sensor_queue, sensor_name):
    global count_transfrom
    global count_img
    global camera_transform
    global veh_transform
    global veh_trans_list_global
    global veh_transform
    global world_map
    global world_waypointlist
    veh_trans_list= []
    veh_location=[]
    veh_rotation=[]
    veh_location.append(veh_transform.location.x)
    veh_location.append(veh_transform.location.y)
    veh_location.append(veh_transform.location.z)
    veh_rotation.append(veh_transform.rotation.pitch)
    veh_rotation.append(0)
    veh_rotation.append(veh_transform.rotation.roll)
    veh_trans_list.append(veh_location)
    veh_trans_list.append(veh_rotation)
    cam_trans_list = []
    cam_location = []
    cam_rotation = []
    cam_location.append(camera_transform.location.x)
    cam_location.append(camera_transform.location.y)
    cam_location.append(camera_transform.location.z-const_z)
    cam_rotation.append(camera_transform.rotation.pitch)
    cam_rotation.append(camera_transform.rotation.yaw)
    cam_rotation.append(camera_transform.rotation.roll)
    cam_trans_list.append(cam_location)
    cam_trans_list.append(cam_rotation)

    if 'camera' in sensor_name:

        if count_img % (7680) == 0 and count_img != 0:  # 67500
            ego_vehicle.destroy()
            camera.destroy()
            print("5")
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)
            print("6")
            #world.tick()
            os._exit(0)
        if count_img % (480) == 0 and count_img != 0:  # 2500

            update_weather_parameters(world)
        if count_img % (16) == 0 and count_img != 0:  #

            veh_transform= ego_vehicle.get_transform()

            transform = random.choice(world_waypointlist).transform
            print(len(world_waypointlist))
            transform.location.z = transform.location.z + 0.015
            print(transform)
            print(transform)
            # veh_trans_list_global = []
            # veh_location=[]
            # veh_rotation=[]wwwwwwwwwwwwwwwwwwwwwwwwwwaaw
            # veh_location.append(transform.location.x)
            # veh_location.append(transform.location.y)
            # veh_location.append(transform.location.z)
            # veh_rotation.append(transform.rotation.pitch)
            # veh_rotation.append(transform.rotation.yaw)
            # veh_rotation.append(transform.rotation.roll)
            # veh_trans_list_global.append(veh_location)
            # veh_trans_list_global.append(veh_rotation)
            # transform.rotation.yaw=0
            ego_vehicle.set_transform(transform)
            spectator.set_transform(carla.Transform(transform.location + carla.Location(z=20),
                                                    carla.Rotation(pitch=-90)))

        # #随机初始化
        # z = random.uniform(3.0,20.0)
        # x = random.uniform(4.0, 15.0)
        # y = random.uniform(4.0, 15.0)
        # # 计算pitch角度（绕Y轴旋转）
        # pitch = math.degrees(math.atan(-z/ abs(-x)))
        # # 计算yaw角度（绕Z轴旋转）
        # yaw = math.copysign(1,-y)*math.degrees(math.acos(-x/(x**2+y**2)**0.5))
        # roll = 0
        # print(x, y, z, pitch, yaw)
        # camera_transform = carla.Transform(carla.Location(x=x ,z=z,y=y), carla.Rotation(pitch=pitch,yaw=yaw,roll=roll))
        #固定参数初始化

        pitch_list = [-22.5, -67.5]
        yaw_list = [0, 45]
        lengths = [5, 10, 15, 20]
        # pitch_list=[0,0,0,0]
        # yaw_list=[90,90,90,90,90,90,90,90]
        # lengths=[10,15,20,30]
        pitch=pitch_list[count_transfrom% len(pitch_list)]
        yaw=yaw_list[count_transfrom//len(pitch_list)%len(yaw_list)]
        roll = 0
        length= lengths[count_transfrom // len(pitch_list)//len(yaw_list) % len(lengths)]
        eulerAngle = Vector3D(pitch, yaw, roll)
        forwardVector = Vector3D(1, 0, 0)
        x,y,z=compute_xyz(eulerAngle,forwardVector,length)
        #print(x,y,z+const_z,pitch,yaw,length,count_img+2)
        camera_transform = carla.Transform(carla.Location(x=x, z=z+const_z, y=y),
                                           carla.Rotation(pitch=pitch, yaw=yaw, roll=roll))
        #计算roll角度（绕X轴旋转）
        camera.set_transform(camera_transform)

        new_img_filename = "data" + str(count_img + 1) + ".png"
        # 使用命令行参数指定的输出目录
        save_path = os.path.join(output_dir,rf'differentColor\{color_name}')
        os.makedirs(save_path, exist_ok=True)
        sensor_data.save_to_disk(os.path.join(save_path, new_img_filename))
        #如果是255,则保存_train
        if color_name=='255,255,255':
            im = cv2.imread(os.path.join(os.path.join(output_dir,rf'differentColor\{color_name}'), new_img_filename))
            im_resized = cv2.resize(im, (800, 800))
            new_filename = "data" + str(count_img + 1) + ".npz"
            dest_path = os.path.join(output_dir,'train', new_filename)
            if not os.path.exists(os.path.dirname(dest_path)):
                os.makedirs(os.path.dirname(dest_path))
            img_data = np.array(im_resized)
            np.savez(dest_path, img=img_data, veh_trans=veh_trans_list, cam_trans=cam_trans_list)
            #img保存到train_new文件夹下
            train_new_path = os.path.join(output_dir,'train_new', new_img_filename)
            if not os.path.exists(os.path.dirname(train_new_path)):
                os.makedirs(os.path.dirname(train_new_path))
            cv2.imwrite(train_new_path, im_resized)
        
    count_transfrom+=1

    if count_transfrom==len(pitch_list)*len(yaw_list)*len(lengths):
        count_transfrom=0
    count_img += 1
    sensor_queue.put((sensor_data.frame, sensor_name))
    # world_empty.tick()
print("1")
client = carla.Client('localhost', 2000)
client.set_timeout(20.0)
world = client.get_world()
world.unload_map_layer(carla.MapLayer.ParkedVehicles)
print("2")
# client_empty = carla.Client('localhost', 6400)
# client_empty.set_timeout(50.0)
# world_empty = client_empty.load_world('Town10HD_Opt')
#
# world_empty.unload_map_layer(carla.MapLayer.Buildings)
# world_empty.unload_map_layer(carla.MapLayer.Decals)
# #world_empty.unload_map_layer(carla.MapLayer.Foliage)
# world_empty.unload_map_layer(carla.MapLayer.ParkedVehicles)
# world_empty.unload_map_layer(carla.MapLayer.StreetLights)
# world_empty.unload_map_layer(carla.MapLayer.Walls)
# world_empty.unload_map_layer(carla.MapLayer.Props)
# world_empty.unload_map_layer(carla.MapLayer.Particles)
# world_empty.unload_map_layer(carla.MapLayer.Foliage)
# world_empty.unload_map_layer(carla.MapLayer.Ground)


try:
    # 设置同步
    print("3")
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 0.1  # 20 fps, 5ms
    world.apply_settings(settings)
    sensor_queue = queue.Queue()
    print("4")
    # settings_empty = world_empty.get_settings()
    # settings_empty.synchronous_mode = True
    # settings_empty.fixed_delta_seconds = 0.1  # 20 fps, 5ms
    # world_empty.apply_settings(settings_empty)
    # 清除场景内所有车
    # 获取场景中所有车辆对象
    actor_list = world.get_actors().filter('vehicle.*')
    # 销毁或删除每个车辆对象
    for vehicle in actor_list:
        vehicle.destroy()  # 销毁车辆对象
    # 天气
    update_weather_parameters(world)
    # 设置同步模式下的自动驾驶
    traffic_manager = client.get_trafficmanager(8000)
    traffic_manager.set_synchronous_mode(True)
    # 拿到这个世界所有物体的蓝图
    blueprint_library = world.get_blueprint_library()
    # 使用命令行传入的车型（vehicle_model）查找蓝图
    ego_vehicle_bp_origin = blueprint_library.find(vehicle_model)
    if ego_vehicle_bp_origin is None:
        print(f"Error: vehicle blueprint '{vehicle_model}' not found in blueprint library.")
        # 打印部分可用车型供参考
        sample = [bp.id for bp in blueprint_library.filter('vehicle.*')][:20]
        print('Sample available vehicle blueprints:', sample)
        sys.exit(1)
    # 给我们的车加上特定的颜色
    ego_vehicle_bp_origin.set_attribute('color', color_name)

    # 拿到这个世界所有物体的蓝图
    # blueprint_library_empty = world_empty.get_blueprint_library()
    # # 从浩瀚如海的蓝图中找到奔驰的蓝图
    # ego_vehicle_bp_empty = blueprint_library_empty.find('vehicle.audi.etron')
    # # 给我们的车加上特定的颜色
    # ego_vehicle_bp_empty.set_attribute('color', '255, 255, 255')

    # 找到所有可以作为初始点的位置并随机选择一个

    #world_map=world.get_map()
    world_map=world.get_map()
    world_waypointlist = world_map.generate_waypoints(2.0)
    transform = random.choice(world_waypointlist).transform
    print(len(world_waypointlist))
    transform.location.z = transform.location.z + 0.015
    print(transform)
    transform_empty=random.choice(world_map.get_spawn_points())
    # 找到一个确定点
    # transform = world.get_map().get_spawn_points()[50]
    # 在这个位置生成汽车

    ego_vehicle = world.spawn_actor(ego_vehicle_bp_origin, transform)

    # veh_trans_list_global = []
    # veh_location = []
    # veh_rotation = []
    # veh_location.append(transform.location.x)
    # veh_location.append(transform.location.y)
    # veh_location.append(transform.location.z)
    # veh_rotation.append(transform.rotation.pitch)
    # veh_rotation.append(transform.rotation.yaw)
    # veh_rotation.append(transform.rotation.roll)
    # veh_trans_list_global.append(veh_location)
    # veh_trans_list_global.append(veh_rotation)
    veh_transform=ego_vehicle.get_transform()
    # ego_vehicle_empty = world_empty.spawn_actor(ego_vehicle_bp_empty, transform_empty)
    # 再给它挪挪窝
    # location = ego_vehicle.get_location()
    # location.x += 10
    # location.y += 10
    # ego_vehicle.set_location(location)
    # 把它设置成自动驾驶模式
    #ego_vehicle.set_autopilot(True, 8000)
    # 我们可以甚至在中途将这辆车“冻住”，通过抹杀它的物理仿真
    #ego_vehicle.set_simulate_physics(False)
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    # camera_empty_bp= blueprint_library_empty.find('sensor.camera.semantic_segmentation')
    IM_WIDTH = 896
    IM_HEIIGHT = 896
    # set the attribute of camera
    camera_bp.set_attribute("image_size_x", f"{IM_WIDTH}")
    camera_bp.set_attribute("image_size_y", f"{IM_HEIIGHT}")
    camera_bp.set_attribute("fov", "90")  # 最好不懂不太懂这个参数
    # camera_empty_bp.set_attribute("image_size_x", f"{IM_WIDTH}")
    # camera_empty_bp.set_attribute("image_size_y", f"{IM_HEIIGHT}")
    # camera_empty_bp.set_attribute("fov", "90")  # 最好不懂不太懂这个参数

    # camera_bp.set_attribute("sensor_tick", "1.0")
    camera_transform = carla.Transform(carla.Location(x=-5.5, z=2.5),carla.Rotation(pitch=8.0))

    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=ego_vehicle)
    # camera_empty=world_empty.spawn_actor(camera_empty_bp, camera_transform, attach_to=ego_vehicle_empty)
    camera.listen(lambda image: sensor_callback(world,camera,ego_vehicle,spectator,image, sensor_queue, "camera"))
    # camera_empty.listen(lambda image: sensor_callback_empty(camera_empty,image, sensor_queue, "camera_empty"))
    spectator = world.get_spectator()
    transform = ego_vehicle.get_transform()
    spectator.set_transform(carla.Transform(transform.location + carla.Location(z=20),
                                            carla.Rotation(pitch=-90)))

    # spectator_empty = world_empty.get_spectator()
    # transform_empty = ego_vehicle_empty.get_transform()
    # spectator_empty.set_transform(carla.Transform(transform_empty.location + carla.Location(z=20),
    #                                               carla.Rotation(pitch=-90)))
    # 如果注销单个Actor
    # ego_vehicle.destroy()
    # 如果你有多个Actor 存在list里，想一起销毁。
    # 程序等待2秒钟，让汽车跑一会儿
    while True:

        world.tick()



        # data = sensor_queue.get(block=True)
        data = sensor_queue.get(block=True)
finally:
    settings = world.get_settings()
    settings.synchronous_mode = False
    settings.fixed_delta_seconds = None
    world.apply_settings(settings)
# import time
# import quaternion
# import carla
# import random
# import os
# import numpy as np
# import queue
# import math
# from PIL import Image, ImageDraw
# from carla import Vector3D
# import cv2
# count_transfrom=0
# count_weather=0
# count_img=0
# const_z=0.812
# count_img_empty=-1
# camera_transform=None
# veh_transform=None
# color_name="255,255,255"
# veh_trans_list_global=[]
# world_map=None
#
# random.seed(0)
# #这个函数是为了找到图像中的红色原点，来调整const_z,因为车辆的中心点在地面上，而想要实现的中心点在车辆中间，在车辆的中心点上方一点点
# def draw_red_origin(file_path):
#     # 打开图像文件
#     image = Image.open(file_path)
#
#     # 获取图像的宽度和高度
#     width, height = image.size
#
#     # 创建一个新的图像对象，用于绘制点
#     new_image = Image.new('RGBA', (width, height))
#     draw = ImageDraw.Draw(new_image)
#
#     # 计算中心点坐标
#     center_x = width // 2
#     center_y = height // 2
#
#     # 绘制红色的原点（半径为3个像素）
#     radius = 1
#     draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), fill=(255, 0, 0))
#
#     # 合并原始图像和绘制的点
#     print(new_image.size,image.convert('RGBA').size)
#     result_image = Image.alpha_composite(image.convert('RGBA'), new_image)
#
#     # 保存结果图像
#     result_file_path = file_path
#     result_image.save(result_file_path)
#
#     return result_file_path
#
# def generate_mask(file_path):
#     # 打开图像文件
#     image = Image.open(file_path)
#     pixels=image.load()
#
#     for i in range(image.width):
#         for j in range(image.height):
#             if pixels[i,j] == (0,0,142,255):
#                 pixels[i,j] = (255,255,255,255)
#             else:
#
#                 pixels[i, j] = (0, 0, 0,255)
#
#     # 保存结果图像
#     result_file_path = file_path
#     image.save(result_file_path)
#
#     return result_file_path
# def update_weather_parameters(world):
#     # 选择要随机更改的参数
#     parameters_to_update = ['fog_density', 'sun_altitude_angle']
#
#     # 在范围内生成随机值
#     fog_density_values = [0.0, 25.0, 50.0, 90]
#     sun_altitude_angle = [-90, -30, 30, 90]
#
#     # 遍历参数列表并随机更改值
#     global count_weather
#
#     fog_density = fog_density_values[(count_weather ) % 4]
#     sun_altitude = sun_altitude_angle[(count_weather//4) % 4]
#
#     weather = carla.WeatherParameters(fog_density=fog_density,
#                                       sun_altitude_angle=sun_altitude)
#
#     print(f"weather change to fog_density: {fog_density}, sun_altitude_angle: {sun_altitude}")
#
#     count_weather += 1
#     world.set_weather(weather)
#
# #计算相机的position
# def compute_xyz(eulerAngle,forwardVector,length):
#     # pitch_radians=math.radians(pitch)
#     # yaw_radians = math.radians(yaw)
#     # tan_yaw=math.tan(yaw_radians)
#     # tan_pitch=math.tan(pitch_radians)
#     # cos_yaw=math.cos(yaw_radians)
#     # sin_yaw=math.sin(yaw_radians)
#     # if yaw!=90 and yaw!=270:
#     #     x=math.copysign(1,cos_yaw)*(length**2/(1+tan_yaw**2+tan_pitch**2))**0.5*-1
#     #     y=abs(x*tan_yaw)*math.copysign(1,sin_yaw)*-1
#     #     z=abs(x*tan_pitch)
#     # else:
#     #     x=0
#     #     z=abs(length*math.sin(pitch_radians))
#     #     y=abs(length*math.cos(pitch_radians))*math.copysign(1,sin_yaw)*-1
#     # return x,y,z
#     pitch=math.radians(eulerAngle.x)
#     yaw=math.radians(eulerAngle.y)
#     roll=math.radians(eulerAngle.z)
#     #direction=(quaternion.Euler(eulerAngle) * Vector3D.forward).normalized
#     dirction_x=math.cos(pitch)*math.cos(yaw)
#     dirction_y=math.cos(pitch)*math.sin(yaw)
#     dirction_z=math.sin(pitch)
#     x=-dirction_x*length
#     y=-dirction_y*length
#     z=-dirction_z*length
#     return x,y,z
# def sensor_callback_empty(camera_empty,image, sensor_queue, sensor_name):
#     global count_img_empty
#     global camera_transform
#     if 'camera' in sensor_name:
#         camera_empty.set_transform(camera_transform)
#         image.convert(carla.ColorConverter.CityScapesPalette)
#         # i = np.array(image.raw_data)
#         # i2 = i.reshape((IM_HEIIGHT, IM_WIDTH, 4))
#         # i3 = i2[:, :, : 3]
#         new_emp_img_filename = "data" + str(count_img_empty + 1) + ".png"
#         image.save_to_disk(os.path.join('../outputs/mask', new_emp_img_filename))
#         #generate_mask(os.path.join('../outputs/mask', '%06d.png' % (count_img_empty+1)))
#     count_img_empty+=1
#     sensor_queue.put((image.frame, sensor_name))
#
#
# def sensor_callback(world,camera,ego_vehicle,spectator,sensor_data, sensor_queue, sensor_name):
#     global count_transfrom
#     global count_img
#     global camera_transform
#     global veh_transform
#     global veh_trans_list_global
#     global veh_transform
#     global world_map
#
#
#     if 'camera' in sensor_name:
#
#         if count_img%(7680)==0 and count_img!=0:#67500
#             exit()
#         if count_img%(480)==0 and count_img!=0:#2500
#
#             update_weather_parameters(world)
#         if count_img%(16)==0 and count_img!=0:#
#             print("w")
#             veh_transform= ego_vehicle.get_transform()
#             transform = random.choice(world_map.get_spawn_points())
#             print(transform)
#
#             ego_vehicle.set_transform(transform)
#             spectator.set_transform(carla.Transform(transform.location + carla.Location(z=20),
#                                                     carla.Rotation(pitch=-90)))
#
#
#         pitch_list=[-22.5,-67.5]
#         yaw_list=[0,45,90,135]
#         lengths=[5,15]
#         pitch=pitch_list[count_transfrom% len(pitch_list)]
#         yaw=yaw_list[count_transfrom//len(pitch_list)%len(yaw_list)]
#         roll = 0
#         length= lengths[count_transfrom // len(pitch_list)//len(yaw_list) % len(lengths)]
#         eulerAngle = Vector3D(pitch, yaw, roll)
#         forwardVector = Vector3D(1, 0, 0)
#         x,y,z=compute_xyz(eulerAngle,forwardVector,length)
#         #print(x,y,z+const_z,pitch,yaw,length,count_img+2)
#         camera_transform = carla.Transform(carla.Location(x=x, z=z+const_z, y=y),
#                                            carla.Rotation(pitch=pitch, yaw=yaw, roll=roll))
#         #计算roll角度（绕X轴旋转）
#         camera.set_transform(camera_transform)
#
#         new_img_filename = "data" + str(count_img + 1) + ".png"
#         sensor_data.save_to_disk(os.path.join(f'../outputs/train/', new_img_filename))
#
#     count_transfrom+=1
#
#     if count_transfrom==len(pitch_list)*len(yaw_list)*len(lengths):
#         count_transfrom=0
#     count_img += 1
#     sensor_queue.put((sensor_data.frame, sensor_name))
#
# client = carla.Client('localhost', 9800)
# client.set_timeout(20.0)
# world = client.get_world()
#
# client_empty = carla.Client('localhost', 9900)
# client_empty.set_timeout(20.0)
# world_empty = client_empty.load_world('Town10HD_Opt')
#
# world_empty.unload_map_layer(carla.MapLayer.Buildings)
# world_empty.unload_map_layer(carla.MapLayer.Decals)
# #world_empty.unload_map_layer(carla.MapLayer.Foliage)
# world_empty.unload_map_layer(carla.MapLayer.ParkedVehicles)
# world_empty.unload_map_layer(carla.MapLayer.StreetLights)
# world_empty.unload_map_layer(carla.MapLayer.Walls)
# world_empty.unload_map_layer(carla.MapLayer.Props)
# world_empty.unload_map_layer(carla.MapLayer.Particles)
# world_empty.unload_map_layer(carla.MapLayer.Foliage)
# world_empty.unload_map_layer(carla.MapLayer.Ground)
#
#
# try:
#     # 设置同步
#     settings = world.get_settings()
#     settings.synchronous_mode = True
#     settings.fixed_delta_seconds = 0.1  # 20 fps, 5ms
#     world.apply_settings(settings)
#     sensor_queue = queue.Queue()
#
#     settings_empty = world_empty.get_settings()
#     settings_empty.synchronous_mode = True
#     settings_empty.fixed_delta_seconds = 0.1  # 20 fps, 5ms
#     world_empty.apply_settings(settings_empty)
#     # 清除场景内所有车
#     # 获取场景中所有车辆对象
#     actor_list = world.get_actors().filter('vehicle.*')
#     # 销毁或删除每个车辆对象
#     for vehicle in actor_list:
#         vehicle.destroy()  # 销毁车辆对象
#     # 天气
#     update_weather_parameters(world)
#     # 设置同步模式下的自动驾驶
#     traffic_manager = client.get_trafficmanager(8000)
#     traffic_manager.set_synchronous_mode(True)
#     # 拿到这个世界所有物体的蓝图
#     blueprint_library = world.get_blueprint_library()
#     # 从浩瀚如海的蓝图中找到奔驰的蓝图
#     ego_vehicle_bp_origin = blueprint_library.find('vehicle.audi.etron')
#     # 给我们的车加上特定的颜色
#     ego_vehicle_bp_origin.set_attribute('color', color_name)
#
#     # 拿到这个世界所有物体的蓝图
#     blueprint_library_empty = world_empty.get_blueprint_library()
#     # 从浩瀚如海的蓝图中找到奔驰的蓝图
#     ego_vehicle_bp_empty = blueprint_library_empty.find('vehicle.audi.etron')
#     # 给我们的车加上特定的颜色
#     ego_vehicle_bp_empty.set_attribute('color', '255, 255, 255')
#
#     # 找到所有可以作为初始点的位置并随机选择一个
#     world_map=world.get_map()
#     transform = random.choice(world_map.get_spawn_points())
#     transform_empty=random.choice(world_empty.get_map().get_spawn_points())
#     # 找到一个确定点
#     # transform = world.get_map().get_spawn_points()[50]
#     # 在这个位置生成汽车
#     ego_vehicle = world.spawn_actor(ego_vehicle_bp_origin, transform)
#
#     # veh_trans_list_global = []
#     # veh_location = []
#     # veh_rotation = []
#     # veh_location.append(transform.location.x)
#     # veh_location.append(transform.location.y)
#     # veh_location.append(transform.location.z)
#     # veh_rotation.append(transform.rotation.pitch)
#     # veh_rotation.append(transform.rotation.yaw)
#     # veh_rotation.append(transform.rotation.roll)
#     # veh_trans_list_global.append(veh_location)
#     # veh_trans_list_global.append(veh_rotation)
#     veh_transform=ego_vehicle.get_transform()
#     ego_vehicle_empty = world_empty.spawn_actor(ego_vehicle_bp_empty, transform_empty)
#     # 再给它挪挪窝
#     # location = ego_vehicle.get_location()
#     # location.x += 10
#     # location.y += 10
#     # ego_vehicle.set_location(location)
#     # 把它设置成自动驾驶模式
#     #ego_vehicle.set_autopilot(True, 8000)
#     # 我们可以甚至在中途将这辆车“冻住”，通过抹杀它的物理仿真
#     #ego_vehicle.set_simulate_physics(False)
#     camera_bp = blueprint_library.find('sensor.camera.rgb')
#     camera_empty_bp= blueprint_library_empty.find('sensor.camera.semantic_segmentation')
#     IM_WIDTH = 896
#     IM_HEIIGHT = 896
#     # set the attribute of camera
#     camera_bp.set_attribute("image_size_x", f"{IM_WIDTH}")
#     camera_bp.set_attribute("image_size_y", f"{IM_HEIIGHT}")
#     camera_bp.set_attribute("fov", "90")  # 最好不懂不太懂这个参数
#     camera_empty_bp.set_attribute("image_size_x", f"{IM_WIDTH}")
#     camera_empty_bp.set_attribute("image_size_y", f"{IM_HEIIGHT}")
#     camera_empty_bp.set_attribute("fov", "90")  # 最好不懂不太懂这个参数
#
#     # camera_bp.set_attribute("sensor_tick", "1.0")
#     camera_transform = carla.Transform(carla.Location(x=-5.5, z=2.5),carla.Rotation(pitch=8.0))
#
#     camera = world.spawn_actor(camera_bp, camera_transform, attach_to=ego_vehicle)
#     camera_empty=world_empty.spawn_actor(camera_empty_bp, camera_transform, attach_to=ego_vehicle_empty)
#     camera.listen(lambda image: sensor_callback(world,camera,ego_vehicle,spectator,image, sensor_queue, "camera"))
#     camera_empty.listen(lambda image: sensor_callback_empty(camera_empty,image, sensor_queue, "camera_empty"))
#     spectator = world.get_spectator()
#     transform = ego_vehicle.get_transform()
#     spectator.set_transform(carla.Transform(transform.location + carla.Location(z=20),
#                                             carla.Rotation(pitch=-90)))
#
#     spectator_empty = world_empty.get_spectator()
#     transform_empty = ego_vehicle_empty.get_transform()
#     spectator_empty.set_transform(carla.Transform(transform_empty.location + carla.Location(z=20),
#                                                   carla.Rotation(pitch=-90)))
#     # 如果注销单个Actor
#     # ego_vehicle.destroy()
#     # 如果你有多个Actor 存在list里，想一起销毁。
#     # 程序等待2秒钟，让汽车跑一会儿
#     while True:
#
#         world.tick()
#         world_empty.tick()
#
#
#         data = sensor_queue.get(block=True)
#         data = sensor_queue.get(block=True)
# finally:
#     settings = world.get_settings()
#     settings.synchronous_mode = False
#     settings.fixed_delta_seconds = None
#     world.apply_settings(settings)
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, send_from_directory, session, redirect, url_for
import netifaces as ni
import subprocess
from datetime import datetime, date
from functools import wraps
import base64
# import hashlib


interface = 'eno1'
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
log_file = os.path.join(log_dir, 'config_server.log')
logger = logging.getLogger('network_logger')
logger.setLevel(logging.INFO)
 
# 创建日志处理器
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
file_handler.setLevel(logging.INFO)
 
# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
 
# 添加日志处理器到logger
if not logger.handlers:
    logger.addHandler(file_handler)



# def calculate_md5(input_str: str, encoding: str = 'utf-8') -> str:
#     """
#     计算字符串的 MD5 哈希值（32位小写）
#     :param input_str: 要计算的字符串
#     :param encoding: 字符串编码（默认 utf-8）
#     :return: 32位小写 MD5 哈希值
#     """
#     # 1. 处理空值（可选，根据业务需求调整）
#     if not isinstance(input_str, str):
#         raise TypeError("输入必须是字符串类型")
    
#     # 2. 编码为字节流（MD5 计算的核心要求）
#     byte_data = input_str.encode(encoding)
    
#     # 3. 创建 MD5 对象并计算哈希
#     md5_obj = hashlib.md5()
#     md5_obj.update(byte_data)
    
#     # 4. 获取 32 位小写十六进制结果（和前端 CryptoJS.MD5 结果一致）
#     md5_hex = md5_obj.hexdigest()
    
#     return md5_hex

def get_network_info(interface):
    try:
        # 检查接口是否存在
        if interface not in ni.interfaces():
            print(f"接口 {interface} 不存在")
            return {
            'ip': f'接口 {interface} 不存在',
            'netmask': '请连接网线',
            'gateway': ''
            # 'interface': interface
        }
        
        # 获取接口的地址信息
        addresses = ni.ifaddresses(interface)
        
        # 检查是否有 IPv4 地址
        if ni.AF_INET not in addresses:
            print(f"接口 {interface} 没有 IPv4 地址")
            return {
            'ip': f'接口 {interface} 没有 IPv4 地址',
            'netmask': '请连接网线',
            'gateway': ''
            # 'interface': interface
        }
        
        # 获取第一个 IPv4 地址信息
        ip_info = addresses[ni.AF_INET][0]
        print(addresses)
        print(ip_info)
        ip = ip_info.get('addr')
        netmask = ip_info.get('netmask')
        
        # 获取网关信息
        gateways = ni.gateways()
        gateway = None

        if ni.AF_INET in gateways:
            print(gateways[ni.AF_INET])
            for (gw_addr, gw_iface, gw_af) in gateways[ni.AF_INET]:
                if gw_iface == interface:
                    gateway = gw_addr
                    break
        else:
            print(f"接口 {interface} 没有获取到网关")
        return {
            'ip': ip,
            'netmask': netmask,
            'gateway': gateway
        }
        
    except Exception as e:
        # print(f"获取网络信息失败: {e}")
        return {
            'ip': f'获取网络信息失败：{e}',
            'netmask': '请连接网线',
            'gateway': '请连接网线'
        }

def get_network_info_multiline(interface):
    """
    返回多行格式的字符串
    """
    info = get_network_info(interface)
    
    if not info:
        return "获取网络信息失败"
    
    # 方法2: 多行格式
    return f"""IP地址: {info['ip']}
子网掩码: {info['netmask']}
网关: {info['gateway'] if info['gateway'] else '未配置'}"""

def set_ip_address(ip, mask, gateway):
    script_path = "/opt/uranus_tools/script/set_ip.sh "
    if mask == '':
        mask = '255.255.255.0'
    command = [script_path + '--ip ' + ip + ' --mask ' + mask]
    if gateway != '':
        command = [script_path + '--ip ' + ip + ' --mask ' + mask + ' --gateway ' + gateway]
    print(command)
    process = subprocess.Popen( command, shell=True)
    process.wait()
    # 记录设置IP地址日志
    logger.info(f"设置IP地址为 {ip}，子网掩码为 {mask}，网关为 {gateway}")

app = Flask(__name__)
app.secret_key = 'uranus_key'
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 30


users = {
    'dXJhbnVz': '7a434bacf66b86c255ab2ce95aa82ae7',
    'eGw=': '5ce3acbc3003dfa69ecce8a9f9e53fa9'
}

@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(session)
        print(args)
        print(kwargs)
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/main_select')
@login_required
def main_select():
    # interface = 'eno1'
    net_info = get_network_info(interface)
    if not net_info:
        return "无法获取网络信息", 500
    print(net_info)
    ip_address = net_info['ip']
    netmask = net_info['netmask']
    gateway = net_info['gateway'] or '未配置'
    return render_template('main_select.html', character_ip=ip_address, character_mask=netmask, character_gateway=gateway)

Exe_folder_path = '/home/uranus/angel/'
Log_folder_path = '/opt/uranus/log/'
Video_folder_path = '/home/uranus/uranus_data/history/'

@app.route('/download')
@login_required
def download_exe_file():
    folder_path = Exe_folder_path
    files = [
        {
            'name': f,
            'mod_time': datetime.fromtimestamp(
                os.path.getmtime(os.path.join(folder_path, f))
            ).strftime('%Y-%m-%d %H:%M:%S'),
            'size': os.path.getsize(os.path.join(folder_path, f))
        }
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    # 按修改时间排序
    files.sort(key=lambda x: os.path.getmtime(
        os.path.join(folder_path, x['name'])
    ), reverse=True)
    return render_template('download.html', files=files, type='exe')

@app.route('/download/video')
@login_required
def download_video_file():
    folder_path = Video_folder_path  # 确保 Video_folder_path 已定义
    
    # 获取今天的日期
    today = date.today()
    
    files = []
    for f in os.listdir(folder_path):
        file_path = os.path.join(folder_path, f)
        
        # 检查是否是文件并且以.mp4结尾（不区分大小写）
        if os.path.isfile(file_path) and f.lower().endswith('.mp4'):
            # 获取修改时间
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            # 检查修改时间是否是今天
            if mod_time.date() == today:
                files.append({
                    'name': f,
                    'mod_time': mod_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'timestamp': os.path.getmtime(file_path),
                    'size': os.path.getsize(file_path)
                })
    
    # 按修改时间排序（最近修改的在前）
    files.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return render_template('download.html', files=files, type='video')
   
@app.route('/download/log')
@login_required
def download_log_file():
    folder_path = Log_folder_path
    today = date.today()

    files = []
    for f in os.listdir(folder_path):
        file_path = os.path.join(folder_path, f)
        
        # 检查是否是文件并且以.mp4结尾（不区分大小写）
        if os.path.isfile(file_path):
            # 获取修改时间
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            # 检查修改时间是否是今天
            if mod_time.date() == today:
                files.append({
                    'name': f,
                    'mod_time': mod_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'timestamp': os.path.getmtime(file_path),
                    'size': os.path.getsize(file_path)
                })
    
    # 按修改时间排序（最近修改的在前）
    files.sort(key=lambda x: x['timestamp'], reverse=True)
    return render_template('download.html', files=files, type='log')

@app.route('/login_check', methods=['POST'])
def login_xl_check():
    print(request.form)
    enusername = request.form['xul']
    enmd5_password = request.form['xpl']

    username = base64.b64decode(enusername).decode('utf-8')
    md5password = base64.b64decode(enmd5_password).decode('utf-8')

    if enusername in users and users[enusername] == md5password:
        # 记录登录成功日志
        logger.info(f"用户 {username} 登录成功")

        session['username'] = enusername
        data = {'success': True, 'message': '登录成功', 'redirect_url': '/main_select'}
        return data
    else:
        data = {'success': False, 'message': '登录失败', 'token': ''}
        # 记录登录失败日志
        logger.warning(f"用户 {username} 登录失败")
        return data


@app.route('/net_settings')
@login_required
def net_settings():
    # interface = 'eno1'
    net_info = get_network_info(interface)
    ip_address = net_info['ip']
    netmask = net_info['netmask']
    gateway = net_info['gateway'] if net_info['gateway'] else ''
    return render_template('set_ip.html', ip_address=ip_address, mask=netmask, gateway=gateway)

@app.route('/reboot_xl')
@login_required
def reboot():
    script_path = "/opt/uranus_tools/script/reboot.sh" 
    process = subprocess.Popen(script_path, shell=True)
    process.wait()
    return '请等待设备重新启动，回到上一个网页，检查IP是否设置成功'

@app.route('/net_config', methods=['POST'])
@login_required
def net_config_xl():
    set_ip = request.form['ipAddress']
    set_mask = request.form['mask']
    set_gateway = request.form['gateway']

    set_ip_address(set_ip, set_mask, set_gateway)

    net_info = get_network_info(interface)
    # 记录设置IP地址日志
    logger.info(f"设置IP地址为 {set_ip}，子网掩码为 {set_mask}，网关为 {set_gateway}")
    cur_ip = net_info['ip']
    cur_mask = net_info['netmask']
    cur_gateway = (net_info['gateway'] if net_info['gateway'] else '未配置')
    logger.info(f"设置后IP地址为 {cur_ip}，子网掩码为 {cur_mask}，网关为 {cur_gateway}")
    return render_template('config.html', set_ip=set_ip, set_mask=set_mask, set_gateway=set_gateway, cur_ip=cur_ip, cur_mask=cur_mask, cur_gateway=cur_gateway)

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/download_/<filename>')
@app.route('/download_exe/<filename>')
@login_required
def download_exe(filename):
    # 记录下载文件日志
    logger.info(f"用户 {session['username']} 下载文件 {filename}")
    return send_from_directory(Exe_folder_path, filename)

@app.route('/download_log/<filename>')
@login_required
def download_log(filename):
    # 记录下载日志文件日志
    logger.info(f"用户 {session['username']} 下载日志文件 {filename}")
    return send_from_directory(Log_folder_path, filename)

@app.route('/download_video/<filename>')
@login_required
def download_video(filename):
    # 记录下载视频文件日志  
    logger.info(f"用户 {session['username']} 下载视频文件 {filename}")
    return send_from_directory(Video_folder_path, filename)



if __name__ == '__main__':

    # ip_address = get_network_info_multiline(interface)
    # if ip_address:
    #     print(f"The IP address of {interface} is: {ip_address}")
    #     app.run(host=ip_address)
    # else:
    #     print(f"Unable to retrieve the IP address of {interface}")
    
    print("==========server start=============")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("服务器启动，监听端口5000")
    info = get_network_info(interface)
    logger.info(f"当前IP地址为 {info['ip']}，子网掩码为 {info['netmask']}，网关为 {info['gateway']}")
    app.run(host='0.0.0.0',port=5000)
    print("==========server stop =============")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("服务器停止")
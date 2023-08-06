from setuptools import setup,find_packages
setup(name='pyscalebox',
      version='0.0.3',
      description='level 2 pipeline api:send_message(body)',
      author='zhangxiaoli',
      author_email='zhangxiaoli@cnic.cn',
      requires=['os','grpc'], # 定义依赖哪些模块
      py_modules=['pyscalebox','control_server_pb2','control_server_pb2_grpc'],  # 系统自动从当前目录开始找包
      # packages=find_packages(),
      license="apache 3.0"
      )
from setuptools import setup, find_packages
 
setup(
    name='acdpnet',
    version='2.0.1',
    description="A TCP Server Frame",
    include_package_data=True,
    author='Aiden Hopkins',#作者
    author_email='acdphc@qq.com',#作者邮件
    maintainer='Aiden Hopkins',#维护者
    maintainer_email='acdphc@qq.com',#维护者邮件
    license='MIT License',#协议
    url='https://github.com/A03HCY/Network-Core',#github或者自己的网站地址
    packages=find_packages(),#包的目录
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
     'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',#设置编写时的python版本
],
    python_requires='>=3.7',#设置python版本要求
    
)
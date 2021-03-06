import os, re, shutil
# #

try:
    internalIp = os.environ['OPENSHIFT_DIY_IP']
    OPENSHIFT_APACH_PORT = os.environ['OPENSHIFT_DIY_PORT']
except:
    try:
        from subprocess import check_output
        import subprocess
        # ip = check_output(["dig", "+short", "@resolver1.opendns.com",
        #                    "myip.opendns.com"]).decode().strip()
        st = """/sbin/ifconfig |grep -B1 "inet addr" |awk '{ if ( $1 == "inet" ) { print $2 } else if ( $2 == "Link" ) { printf "%s:" ,$1 } }' |awk -F: '{ print $1 ": " $3 }'"""
        output = subprocess.Popen([st], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        ip2 = output.communicate()[0]
        print
        ip2.rstrip()
        internalIp = ip2.split('lo:')[1].replace(' ', '')
        print internalIp
    except:
        print 'We could not find internal ip of your app or your system,' \
        'problem maybe ocurred because this is working by linux system and you are using windows system'
        print
        '\n So we use ip="127.0.0.1" as your free internal for setting nginx listen to it ip !!!!!!!!'
        internalIp = '127.0.0.1'
        OPENSHIFT_APACH_PORT='8080'

CurrentDir = os.path.dirname(os.path.realpath(__file__))
Parent_Dir = os.path.abspath(os.path.join(CurrentDir, '..'))
try:
    runtimeDir = os.environ['OPENSHIFT_HOMEDIR'] + "/app-root/runtime"
    repoDir = os.environ['OPENSHIFT_HOMEDIR'] + "/app-root/runtime/repo/openshift-diy-php"
    Bash_File = os.environ['OPENSHIFT_HOMEDIR'];Gear_DNS=os.environ['OPENSHIFT_GEAR_DNS']
except:
    os.environ['OPENSHIFT_HOMEDIR'] = Parent_Dir;Gear_DNS='127.0.0.1'
    runtimeDir = os.environ['OPENSHIFT_HOMEDIR'] + "/app-root/runtime"
    # repoDir = os.environ['OPENSHIFT_HOMEDIR'] + "/app-root/runtime/repo/openshift-diy-php"
    repoDir = os.path.abspath(os.path.join(Parent_Dir, '..'))
    Bash_File = os.environ['OPENSHIFT_HOMEDIR']
    # if not os.path.isdir(runtimeDir):
    #     os.mkdir(runtimeDir)
    if not os.path.isdir(repoDir):
        os.mkdir(repoDir)



# CurrentDir = os.path.dirname(os.path.realpath(__file__))
# Parent_Dir = os.path.abspath(os.path.join(CurrentDir, '..'))
www_Gear_DNS='www'+Gear_DNS
from sys import platform as _platform

if _platform == "linux" or _platform == "linux2":
    # linux
    print    'we are using linux '
elif _platform == "darwin":
    # OS X
    print    'we are using OS X '
elif _platform == "win32":
    # Windows...
    print    'we are using Windos '
    Parent_Dir = Parent_Dir.replace('\\', '/')
    repoDir = repoDir.replace('\\', '/')
    Bash_File = Bash_File.replace('\\', '/')
    runtimeDir = runtimeDir.replace('\\', '/')

Destination = repoDir
print Parent_Dir

## copy file_source Contains to File_Target if is not similar and make it if
# there is no target file

def replace(file_pattern, file_target):
    # Read contents from file_target as a single string
    if os.path.isfile(file_target):
        pass
    else:
        file_pattern2 = open(file_pattern, 'r')
        pattern = file_pattern2.readlines()
        file_pattern2.close()

        file_handle2 = open(file_target, 'wb')
        file_handle2.writelines(pattern)
        file_handle2.close()

    file_handle = open(file_target, 'r')
    # file_string1 = file_handle.read()
    file_string = file_handle.readlines()
    file_handle.close()
    file_pattern2 = open(file_pattern, 'r')
    pattern = file_pattern2.readlines()
    file_pattern2.close()
    file_handle2 = open(file_target, 'a+b')
    i = -1
    t = -1
    for line in range(i + 1, len(pattern)):
        I_S = 0
        for j in range(t + 1, len(file_string)):
            if pattern[line] in file_string[j]:
                I_S = 1
                break
            else:
                pass
        if I_S == 0:
            file_handle2.writelines(pattern[line])
    file_handle2.close()

## copy new files and strings to destination
for root, dirs, files in os.walk(Parent_Dir):
    curent_path0 = root.split(Parent_Dir)[1] + '/'
    curent_path = curent_path0.replace('\\', '/')
    root = root.replace('\\', '/')
    for dir2 in dirs:
        if os.path.isdir(Destination + curent_path + dir2):
            pass
        else:
            if not os.path.isdir(Destination): os.mkdir(Destination)
            os.mkdir(Destination + curent_path + dir2)
    for file2 in files:
        if os.path.isfile(Destination + curent_path + file2):
            path = os.path.join(root, file2)
            path2=path.replace('\\', '/')
            # size_source = os.stat(path.replace('\\', '/')).st_size # in bytes
            size_source = os.stat(path2).st_size # in bytes
            size_target = os.stat(Destination + curent_path + file2).st_size
            if size_source != size_target:
                replace(Parent_Dir + curent_path + file2, Destination + curent_path + file2)
        else:
            replace(Parent_Dir + curent_path + file2, Destination + curent_path + file2)

try:
    replace(Parent_Dir + "/misc/templates/bash_profile.tpl", Bash_File + '/app-root/data/.bash_profile')
except:
    # replace(Parent_Dir + "/misc/templates/bash_profile.tpl", Bash_File + '/app-root/data/.bash_profile')
    print """ we couldn't replace bash profile ,
    \nSo maybe some vaiable couldnt accessed when you conected by ssh and using bash , and No more"""




f = open(repoDir + '/misc/templates/httpd.conf.tpl', 'r')
conf_httpd = f.read().replace('{{OPENSHIFT_INTERNAL_IP}}', internalIp).replace('{{OPENSHIFT_REPO_DIR}}', repoDir)\
    .replace('{{OPENSHIFT_RUNTIME_DIR}}', runtimeDir).replace('{{OPENSHIFT_APACH_PORT}}', OPENSHIFT_APACH_PORT)

f.close()

f = open(runtimeDir + '/srv/httpd/conf/httpd.conf', 'w')
# f = open(repoDir+'/httpd.conf.tpl'  , 'w')
f.write(conf_httpd)
f.close()

f = open(repoDir + '/misc/templates/php.ini.tpl', 'r')
conf_php = f.read().replace('{{OPENSHIFT_INTERNAL_IP}}', internalIp).replace('{{OPENSHIFT_REPO_DIR}}', repoDir).replace(
    '{{OPENSHIFT_RUNTIME_DIR}}', runtimeDir)
f.close()

f = open(runtimeDir + '/srv/php/etc/apache2/php.ini', 'w')
f.write(conf_php)
f.close()


f = open(repoDir + '/misc/templates/php.ini.tpl', 'r')
conf_php = f.read().replace('{{OPENSHIFT_INTERNAL_IP}}', internalIp).replace('{{OPENSHIFT_REPO_DIR}}', repoDir).replace(
    '{{OPENSHIFT_RUNTIME_DIR}}', runtimeDir)
f.close()

f = open(runtimeDir + '/srv/php/etc/apache2/php.ini', 'w')
f.write(conf_php)
f.close()


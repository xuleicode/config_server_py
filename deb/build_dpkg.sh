#!/bin/bash

echo ====begin $0
dirname=$(cd `dirname $0`; pwd)
echo $dirname

product_name="uranus-tools-server"
package_name=uranus_tools_server
echo "deb package..."
target_name=${product_name}_arm64.deb
version=0.2.0.0001
if [ -n "$1" ];then
    target_name=${product_name}_$1_arm64.deb
    echo "target_name" $target_name
    version=$1
fi

jetson_ver="6.2"
depend_ver=">=36"



package_dir=debtemp


echo "calculate package size..."
deploySize=$(du -s $dirname/${package_dir})
packSize="`echo $deploySize | cut -d ' ' -f 1`"
echo package: ${packSize}
sed -i "s/&size/$packSize/" $dirname/${package_dir}/DEBIAN/control
sed -i "s/&version/$version/" $dirname/${package_dir}/DEBIAN/control
sed -i "s/&package_name/$package_name/" $dirname/${package_dir}/DEBIAN/control
sed -i "s/&product_name/$product_name/" $dirname/${package_dir}/DEBIAN/control
sed -i "s/&jetson_ver/$jetson_ver/" $dirname/${package_dir}/DEBIAN/control
sed -i "s/&depend_ver/$depend_ver/" $dirname/${package_dir}/DEBIAN/control

echo "$(tput blink)$(tput setaf 1)If necessary, please input  password for root$(tput sgr0)"
echo "uranus" | sudo -S chmod 755 $dirname/${package_dir}/DEBIAN/postinst
sudo chmod 755 $dirname/${package_dir}/DEBIAN/postrm
sudo chmod 755 $dirname/${package_dir}/DEBIAN/prerm
sudo chmod 755 $dirname/${package_dir}/DEBIAN/preinst
sudo chmod 755 $dirname/${package_dir}/opt/uranus_tools

echo "$(tput blink)$(tput setaf 1)====packing...====$(tput sgr0)"
rm -f $dirname/../${target_name}
cd ${dirname}
dpkg -b $dirname/${package_dir} $dirname/../${target_name}

echo   ====
cd $dirname/..
ls -lh ${target_name}
echo   "====`date`===="
echo Got the installation package: `realpath ${target_name}`

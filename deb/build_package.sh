#!/bin/bash
echo ====begin $0

version=0.2.0
BUILD_NUMBER=1001
product_name=uranus
project_name=uranus
package_name=uranus
build_version=$version.$BUILD_NUMBER

echo_tput() {
    echo "$(tput blink)$(tput setaf 1)$*$(tput sgr0)"
}
check_files() {
    file_array=(
        main_app.py
    )

    echo "check files  $0 $1"

    echo "file number: ${#file_array[*]}"
    echo "files: ${file_array[*]}"


    for file in ${file_array[@]}
    do
        file_path=${uranus_dir}/${file}
        if [ -f ${file_path} ]; then
            ls -l ${file_path} #strip --strip-unneeded  -o ${file_path}_striped $file_path
        else
        #if [ ! -f ${uranus_dir}/${file} ]; then
            echo_tput "${file_path} not found"
            exit 1
        fi
    done
}


if [ -n "$1" ]; then
    build_version=$1
fi

sk_dir=sk_breast

jetson_ver="6.2"

target_name=${product_name}_${build_version}_arm64.deb

path=`realpath $0`
rdir=`dirname $path`

echo ${rdir}
temp_dir_name=debtemp
temp_dir=${rdir}/${temp_dir_name}
uranus_dir=${temp_dir}/opt/uranus_tools


rm -rf ${temp_dir}
echo  ====remove ${temp_dir}
cp -rf ${rdir}/debPackage ${temp_dir}

cp -rf ${rdir}/../file_server/* ${uranus_dir}/
chmod +x ${uranus_dir}/start_server.sh
chmod +x ${uranus_dir}/main_app.py
chmod +x ${uranus_dir}/script/set_ip.sh
chmod +x ${uranus_dir}/script/reboot.sh
chmod +x ${temp_dir}/etc/init.d/start_uranus_tools_server.sh
#校验文件
check_files ${jetson_ver}
echo "build package succeed====`date`==="

#日志
log_path=${target_name}_file.list
echo "`date`" > ${log_path}
echo "${target_name}" >> ${log_path}
tree ${uranus_dir} >> ${log_path}
echo "" >> ${log_path}
echo "===md5===      ===file name===" >> ${log_path}
find ${uranus_dir} -type f -exec md5sum {} \; >> ${log_path}

#修改安装包信息、打包
chmod +x ${rdir}/build_dpkg.sh
bash ${rdir}/build_dpkg.sh $build_version $product_name $package_name $jetson_ver ${temp_dir_name}

#!/bin/sh

# 参数解析
parse_arguments() {
    while [ $# -gt 0 ]; do
        case $1 in
            --ip)
                if [ -n "$2" ]; then
                    IP_ADDR="$2"
                    shift 2
                else
                    echo "错误: --ip 需要一个参数"
                    exit 1
                fi
                ;;
            --mask)
                if [ -n "$2" ]; then
                    if validate_ip "$2"; then
                        NETMASK="$2"
                    fi
                    shift 2
                else
                    echo "错误: --mask 需要一个参数"
                    exit 1
                fi
                ;;
            --gateway)
                if [ -n "$2" ]; then
                    GATEWAY="$2"
                    shift 2
                else
                    echo "错误: --gateway 需要一个参数"
                    exit 1
                fi
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "未知参数: $1"
                exit 1
                ;;
        esac
    done
}

# 显示帮助
show_help() {
    echo "用法: $0 --ip IP地址 [--mask 子网掩码] [--gateway 网关]"
    echo "示例: $0 --ip 192.168.1.100 --mask 255.255.255.0 --gateway 192.168.1.1"
}

# 验证IP地址格式
validate_ip() {
    local ip="$1"
    
    # 检查格式
    echo "$ip" | grep -qE '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'
    if [ $? -ne 0 ]; then
        return 1
    fi
    
    # 检查每个部分是否在0-255之间
    OLDIFS="$IFS"
    IFS="."
    set -- $ip
    IFS="$OLDIFS"
    
    for part in "$@"; do
        if [ "$part" -lt 0 ] || [ "$part" -gt 255 ]; then
            return 1
        fi
    done
    
    return 0
}

mask_to_cidr() {
    mask=$1
    cidr=0
    
    # 使用tr将点替换为空格，然后使用for循环遍历
    for octet in $(echo $mask | tr '.' ' '); do
        case $octet in
            255) cidr=$((cidr + 8)) ;;
            254) cidr=$((cidr + 7)) ;;
            252) cidr=$((cidr + 6)) ;;
            248) cidr=$((cidr + 5)) ;;
            240) cidr=$((cidr + 4)) ;;
            224) cidr=$((cidr + 3)) ;;
            192) cidr=$((cidr + 2)) ;;
            128) cidr=$((cidr + 1)) ;;
            0) ;;
            *) 
                echo "错误: 无效的子网掩码: $octet"
                return 1
                ;;
        esac
    done
    
    echo $cidr
}

# 主函数
main() {
    # 默认值
    IP_ADDR=""
    NETMASK="255.255.255.0"
    GATEWAY=""
    
    # 如果没有参数，显示帮助
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi
    
    # 解析参数
    parse_arguments "$@"

    

    CIDR=$(mask_to_cidr "$NETMASK")
    echo "子网掩码: $NETMASK (CIDR: $CIDR)"
    
    # 检查必须参数
    if [ -z "$IP_ADDR" ]; then
        echo "错误: 必须指定IP地址 (--ip)"
        exit 1
    fi
    
    # 验证IP地址
    if ! validate_ip "$IP_ADDR"; then
        echo "错误: IP地址格式不正确: $IP_ADDR"
        exit 1
    fi

    echo "IP地址: $IP_ADDR/$CIDR"

    
    # 如果提供了网关，验证它
    if [ -n "$GATEWAY" ] && validate_ip "$GATEWAY"; then
        echo "设置网关地址: $GATEWAY"
        echo 'uranus' | sudo -S nmcli connection modify "Wired connection 1" ipv4.gateway "$GATEWAY"
    fi

    echo 'uranus' | sudo -S nmcli connection modify "Wired connection 1" ipv4.address "$IP_ADDR/$CIDR"

    
    # 显示配置信息
    echo "=== 网络配置 ==="
    echo "IP地址: $IP_ADDR/$CIDR"
    echo "子网掩码: $NETMASK"
    if [ -n "$GATEWAY" ]; then
        echo "网关: $GATEWAY"
    else
        echo "网关: (未设置)"
    fi

    echo 'uranus' | sudo -S nmcli connection up "Wired connection 1"
}

# 执行主函数
main "$@"
#!/bin/bash
set -x

# 需要设置环境变量
# REPORT_ADDR : 用来报告运行接口的回调地址， restful形式    给后台
# INPUT_ADDR : 用来获取输入数据， restful形式              数据湖地址
# OUTPUT_ADDR : 用来输出数据， restful形式                 数据湖地址2
# INPUT_MODEL_ID : 数据湖输入模型id
# OUTPUT_DATA_SOURCE_ID : 数据湖输出数据源id
# BATCH_FORMAT : 批处理任务调度格式， crontab格式
# INSTANCE_ID: 实例ID
# INFER_ID: 推理id
# TRAINER_ID: 训练id
# TOKEN: token
# TENANT_ID: 租户id
# PERODIC_INTERVAL: 状态信息定时上报间隔
# DATA_SOURCE_READ_SIZE: 一次性读取数据源数据大小
# DATA_SOURCE_READ_LIMIT: 最多读取数据源数据大小
# API_EXTRAINFO: api接口增加额外信息， 比如 API_EXTRAINFO=1 返回 {"extrainfo":{"status":500, "message":"er"}, "data":data} ,否则返回 {"data": data}
# ERR_MASSAGE: 错判信息， 由框架写入环境变量， 然后脚本上报

REPORTCODE=$1

function get_report_type() {
    if [ "$REPORTCODE" == "importmodel" ]; then
        echo "importmodel"
    elif [ "$REPORTCODE" == "importalg" ]; then
        echo "importalg"
    elif [ "$REPORTCODE" == "train" ]; then
        echo "train_fail"
    elif [ "$REPORTCODE" == "batchservice" ] || [ "$REPORTCODE" == "allserver" ]; then
        echo "batchjob-"$TASK
    elif [ "$REPORTCODE" == "apiserver" ]; then
        echo "inferstatus"
    else
        echo "unknow"
    fi
}
REPORTTYPE=$(get_report_type)


if [[ "$PERODIC_INTERVAL" -eq "" ]]; then
    export PERODIC_INTERVAL=10
    echo '设置状态信息定时上报间隔' $PERODIC_INTERVAL
fi

function caught_error() {
    if [[ -n "$REPORT_ADDR" ]]; then
        message=$1
        if [[ -z "$message" ]]; then
            curl -s -o /dev/nul -H "Content-Type:application/json" -X POST --data "{\"id\":\"$INSTANCE_ID\",\"code\":500,\"token\":\"$TOKEN\",\"type\":\"$REPORTTYPE\",\"message\":\"$ERR_MASSAGE\",\"data\":\"\"}" $REPORT_ADDR
        else
            curl -s -o /dev/nul -H "Content-Type:application/json" -X POST --data $message $REPORT_ADDR
        fi
    fi
}

function report_error() {
    if [ "$1" != "0" ]; then
        # 报错分析
        if [ "$1" == "137" ]; then
            message="Process finished with exit code 137: Out Of Memory"
        else 
            message="Process finished with Error: $1, function $2, occurred on $3"
        fi

        # 上报报错
        if [[ -n "$REPORT_ADDR" ]]; then
            curl -s -o /dev/nul -H "Content-Type:application/json" -X POST --data "{\"id\":\"$INSTANCE_ID\",\"code\":500,\"token\":\"$TOKEN\",\"type\":\"$REPORTTYPE\",\"message\":\"$message\",\"data\":\"\"}" "$REPORT_ADDR"
        else
            echo "$message"
        fi
    fi
}

export PYTHONPATH=/root # PYTHONPATH is the default search path of Python
trap 'report_error $? $FUNCNAME $LINENO' CHLD ILL


getpackage() {
    cd /root/
    if [[ -f "/root/packages/algorithm.py" ]]; then
        echo /root/packages
    else
        for l in $(ls -1 /root/packages); do
            if [[ -f "/root/packages/$l/algorithm.py" ]]; then
                echo /root/packages/$l
                break
            fi
        done
    fi
    echo ''
}

getRowAddress() {
    if [[ $SOURCE_TYPE == 4 ]] || [[ $SOURCE_TYPE == 5 ]]; then
        echo $INPUT_GETROW_ADDR
    else
        echo $INPUT_GETROW_ADDR'/'$INPUT_MODEL_ID'/null'
    fi
}

import() {
    cd /root/
    l=$(getpackage)
    r_file=$l/requirements.txt
    
    # run 'getpackage' function and get a dir path '/root/packages/car_recognize'
    if [ -f "$r_file" ]; then
        python -m pip install -i $PYPI_SOURCE --trusted-host $PYPI_HOST -r $r_file
    fi

    cd $l # python会读取项目启动时当前目录作为工作路径，如果不进到算法的包里，很容易导致算法的相对路径全部失效
    if [[ -n "$REPORT_ADDR" ]]; then
        python /root/intelliw/interface/controller.py -m $1 -p $l -r $REPORT_ADDR
    else
        python /root/intelliw/interface/controller.py -m $1 -p $l
    fi

    if [[ $? != 0 ]]; then
        caught_error "{\"id\":\"$INSTANCE_ID\",\"code\":500,\"token\":\"$TOKEN\",\"type\":\"$REPORTTYPE\",\"message\":\"$ERR_MASSAGE\",\"data\":\"\"}"
    fi
}

importmodel() {
    import importmodel
}

importalg() {
    import importalg
}

apiservice() {
    l=$(getpackage)

    cd $l
    if [[ -n "$REPORT_ADDR" ]]; then
        python /root/intelliw/interface/controller.py -m apiservice -p $l -r $REPORT_ADDR
    else
        python /root/intelliw/interface/controller.py -m apiservice -p $l
    fi
}

validateservice() {
    l=$(getpackage)
    cd $l
    if [[ -n "$REPORT_ADDR" ]]; then
        python /root/intelliw/interface/controller.py -m validateservice -n validate -p $l -r $REPORT_ADDR
    else
        python /root/intelliw/interface/controller.py -m validateservice -n validate -p $l
    fi
    if [[ $? != 0 ]]; then
        caught_error "{\"id\":\"$INSTANCE_ID\",\"code\":500,\"token\":\"$TOKEN\",\"type\":\"$REPORTTYPE\",\"message\":\"$ERR_MASSAGE\",\"data\":\"\"}"
    fi
}

batchservice() {
    l=$(getpackage)
    if [[ -n "$INPUT_ADDR" ]] && [[ -n "$OUTPUT_ADDR" ]] && [[ -n "$TASK" ]]; then
        final_getrow_address=$(getRowAddress)
        cd $l
        if [[ -n "$REPORT_ADDR" ]]; then
            python /root/intelliw/interface/controller.py -m batchservice -p $l -t $TASK -i $INPUT_ADDR -o $OUTPUT_ADDR -r $REPORT_ADDR -w $final_getrow_address -f "$BATCH_FORMAT"
        else
            python /root/intelliw/interface/controller.py -m batchservice -p $l -t $TASK -i $INPUT_ADDR -o $OUTPUT_ADDR -w $final_getrow_address -f "$BATCH_FORMAT"
        fi
    else
        caught_error "{\"id\":\"$INSTANCE_ID\",\"code\":500,\"token\":\"$TOKEN\",\"type\":\"$REPORTTYPE\",\"message\":\"$ERR_MASSAGE\",\"data\":\"\"}"
    fi
}

allservice() {
    #    set -m
    l=$(getpackage)
    export TASK=infer

    echo "开始api服务"

    cd $l
    if [[ -n "$REPORT_ADDR" ]]; then
        python /root/intelliw/interface/controller.py -m apiservice -p $l -r $REPORT_ADDR &
    else
        python /root/intelliw/interface/controller.py -m apiservice -p $l &
    fi

    echo "开始批处理服务"
    if [[ -n "$INPUT_ADDR" ]] && [[ -n "$OUTPUT_ADDR" ]] && [[ -n "$TASK" ]]; then
        final_getrow_address=$(getRowAddress)
        cd $l
        if [[ -n "$REPORT_ADDR" ]]; then
            python /root/intelliw/interface/controller.py -m batchservice -p $l -t $TASK -i $INPUT_ADDR -o $OUTPUT_ADDR -r $REPORT_ADDR -w $final_getrow_address -f "$BATCH_FORMAT" &
        else
            python /root/intelliw/interface/controller.py -m batchservice -p $l -t $TASK -i $INPUT_ADDR -o $OUTPUT_ADDR -w $final_getrow_address -f "$BATCH_FORMAT" &
        fi
    else
        caught_error "{\"id\":\"$INSTANCE_ID\",\"code\":500,\"token\":\"$TOKEN\",\"type\":\"$REPORTTYPE\",\"message\":\"$ERR_MASSAGE\",\"data\":\"\"}"
    fi

    wait # wait for all subshells to finish
    #    set +m
}

train() {
    l=$(getpackage)
    export TASK=train
    if [[ -n "$INPUT_ADDR" ]] && [[ -n "$TASK" ]]; then
        final_getrow_address=$(getRowAddress)
        cd $l
        if [[ -n "$REPORT_ADDR" ]]; then
            python /root/intelliw/interface/controller.py -m batchservice -p $l -t $TASK -i $INPUT_ADDR -o $OUTPUT_ADDR -r $REPORT_ADDR -w $final_getrow_address -f "$BATCH_FORMAT"
        else
            python /root/intelliw/interface/controller.py -m batchservice -p $l -t $TASK -i $INPUT_ADDR -o $OUTPUT_ADDR -w $final_getrow_address -f "$BATCH_FORMAT"
        fi
    fi

    if [[ $? != 0 ]]; then
        caught_error "{\"id\":\"$INSTANCE_ID\",\"code\":500,\"token\":\"$TOKEN\",\"type\":\"$REPORTTYPE\",\"message\":\"$ERR_MASSAGE\",\"data\":\"\"}"
    fi
}

case $REPORTCODE in
importmodel)
    importmodel
    ;;
importalg)
    importalg
    ;;
train)
    train
    ;;
apiservice)
    apiservice
    ;;
batchservice)
    batchservice
    ;;
allservice)
    allservice
    ;;
kill)
    terminate
    ;;
validateservice)
    validateservice
    ;;
*)
    echo -e "no parameter"
    ;;
esac
exit 0

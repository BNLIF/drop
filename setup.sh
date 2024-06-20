# enter environment
#source env/bin/activate

# get the directory of this setup.sh script
DROP_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

#export SOURCE_DIR="${DROP_DIR}/src/"
#export YAML_DIR="${DROP_DIR}/yaml/"
#export LIB_DIR="${DROP_DIR}/lib/"
#export TOOL_DIR="${DROP_DIR}/tools/"
export SOURCE_DIR="/home/wangbtc/drop/src"
export YAML_DIR="/home/wangbtc/drop/yaml"
export LIB_DIR="/home/wangbtc/drop/lib"
export TOOL_DIR="/home/wangbtc/drop/tools"
# Print the environment variables to stdout
echo "SOURCE_DIR=$SOURCE_DIR"
echo "YAML_DIR=$YAML_DIR"
echo "LIB_DIR=$LIB_DIR"
echo "TOOL_DIR=$TOOL_DIR"

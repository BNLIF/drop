# enter environment
#source env/bin/activate

# get the directory of this setup.sh script
DROP_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

export SOURCE_DIR="${DROP_DIR}/src"
export YAML_DIR="${DROP_DIR}/yaml"

#!/bin/bash +x
# This script is meant to build and test the FW image
# on an RPU simulator using the Univa Grid Engine.
# The default shell is assumed to be bash.

BUILD_TYPE=$1
EN_TEST=$2

SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
PHY_DIR=$SCRIPT_PATH/..
echo SCRIPT_PATH = $SCRIPT_PATH
echo PHY_DIR=$PHY_DIR

# Setting up environment variables for toolkits and python
if [ `hostname` == 'hyd-node-01.nordicsemi.no' ]; then
   echo Setting env variables for `hostname`
   toolsDir=/home/user/tools
   export PYTHONPATH=$toolsDir/python/2.7.18
   export PATH=$PYTHONPATH/bin:$PATH
   export PATH=$toolsDir/codescape/Codescape-8.6/:$PATH
   export MIPS_ELF_ROOT=$toolsDir/mips/Toolchains/mips-mti-elf/2017.10-05
   export MIPS_MTI_ROOT=$MIPS_ELF_ROOT
   export UCC_INST_ROOT=$toolsDir/uccToolkit/7.4.0
   export PLATFORM_API_ROOT=$UCC_INST_ROOT/src/uccPlatform/vendorPkgs
   export PATH=$UCC_INST_ROOT/bin:$PATH
   export JAVA_HOME=/usr/

   # TODO: We need find a way to copy Matlab executable.

elif [ `hostname` == 'jenkinsworker3.nordicsemi.no' ]; then
   echo Setting env variables for `hostname`
   PROJ_DIR=/projects01/ensigma/systems/
   toolsDir=/projects01/ensigma/systems/tools
   export PYTHONPATH=$toolsDir/python/2.7.18
   export PATH=$PYTHONPATH/bin:$PATH
   export PATH=$toolsDir/codescape/Codescape-8.6/:$PATH
   export MIPS_ELF_ROOT=$toolsDir/mips/Toolchains/mips-mti-elf/2017.10-05
   export MIPS_MTI_ROOT=$MIPS_ELF_ROOT
   export UCC_INST_ROOT=$toolsDir/uccToolkit/7.4.0
   export PLATFORM_API_ROOT=$UCC_INST_ROOT/src/uccPlatform/vendorPkgs
   export PATH=$UCC_INST_ROOT/bin:$PATH
   export JAVA_HOME=/pro/jenkins/bin/java/current

   # Copy Matlab exe folder
   # MAT_EXE_DIR_SRC=bin_1098_5910725
   # MAT_EXE_DIR_SRC=$PROJ_DIR/reg/$MAT_EXE_DIR_SRC
   # cp $MAT_EXE_DIR_SRC $TEST_DIR/matlab_exe_lin -rTf
else
   BUILD_DIR=$PHY_DIR/harness/loader/build/smake
   PROJ_DIR=/pro/ensigma/systems
   toolsDir=/projects01/ensigma/systems/tools
   export PYTHONPATH=$toolsDir/python/2.7.18
   export PATH=$PYTHONPATH/bin:$PATH
   export UCC_INST_ROOT=$toolsDir/uccToolkit/7.4.0
   export PLATFORM_API_ROOT=$UCC_INST_ROOT/src/uccPlatform/vendorPkgs
   export MIPS_ELF_ROOT=$toolsDir/mips/Toolchains/mips-mti-elf/2017.10-05
   export MIPS_MTI_ROOT=$MIPS_ELF_ROOT
   export PATH=$UCC_INST_ROOT/bin:$PATH

   # Copy Matlab exe folder
   MAT_EXE_DIR_SRC=bin_2010_5924530
   MAT_EXE_DIR_SRC=$PROJ_DIR/reg/$MAT_EXE_DIR_SRC
   cp $MAT_EXE_DIR_SRC $PHY_DIR/matlab_exe_lin -rTf

fi

#  ------- Python version ------------------------------------
echo `python --version` used from `which python`
echo smake used: `which smake`
echo java used is $JAVA_HOME/bin/java `$JAVA_HOME/bin/java -version`

# ------ Build the image in build directory and return ------
echo Building for $BUILD_TYPE
if [ "$BUILD_TYPE" = "FPGA_B0" ]; then
    BUILD_DIR=$PHY_DIR/harness/loader/build/smake
    cd $BUILD_DIR
    smake \
       CONFIG=release  \
       TARGET=CORE     \
       SOC=1X1AX_20MHZ \
       TEST_SETUP=FPGA \
       RF=GEN2TC_B0    \
       AFE=NORMAL      \
       MAC_HW=ENABLE wipef all
    rc1=$?

elif [ "$BUILD_TYPE" = "FPGA_B0_TX" ]; then
    BUILD_DIR=$PHY_DIR/harness/loader/build/smake
    cd $BUILD_DIR
    smake \
       CONFIG=release  \
       TARGET=CORE     \
       SOC=1X1AX_20MHZ \
       TEST_SETUP=FPGA \
       RF=GEN2TC_B0    \
       AFE=NORMAL      \
       wipef all
    rc1=$?

elif [ "$BUILD_TYPE" = "FPGA_C0" ]; then
    BUILD_DIR=$PHY_DIR/harness/loader/build/smake
    cd $BUILD_DIR
    smake \
       CONFIG=release         \
       TARGET=CORE            \
       SOC=1X1AX_20MHZ        \
       TEST_SETUP=FPGA        \
       RF=GEN2TC_C0           \
       AFE=NORMAL             \
       MAC_HW=ENABLE wipef all
    rc1=$?

elif [ "$BUILD_TYPE" = "FPGA_C0_TX" ]; then
    BUILD_DIR=$PHY_DIR/harness/loader/build/smake
    cd $BUILD_DIR
    smake \
       CONFIG=release         \
       TARGET=CORE            \
       SOC=1X1AX_20MHZ        \
       TEST_SETUP=FPGA        \
       RF=GEN2TC_C0           \
       AFE=NORMAL             \
       wipef all
    rc1=$?

elif [ "$BUILD_TYPE" = "SIM" ]; then
    echo Building code ...
    cd $BUILD_DIR
    smake \
       CONFIG=release    \
       TARGET=CORE       \
       SOC=1X1AX_20MHZ   \
       TEST_SETUP=SIM    \
       AFE=PLAYOUT       \
       MAC_HW=ENABLE     \
       all
    rc1=$?

elif  [ "$BUILD_TYPE" = "SIM_TX" ]; then
    echo Building code ...
    cd $BUILD_DIR
    smake \
       CONFIG=release    \
       TARGET=CORE       \
       SOC=1X1AX_20MHZ   \
       TEST_SETUP=SIM    \
       AFE=PLAYOUT       \
       all
    rc1=$?

else
    echo 'Not building firmware code.'
fi

# ------ If testing is enabled, do that. ------
if [ "$EN_TEST" == "true" ]; then

    # The following is required to locate the RPU simulators.
    if [ "$USER" == "jenkins" ]; then
        # Message from simulator installation.
        # Ensure the environment variable IMGTEC_USER_HOME is set to: 
	    #   /projects01/ensigma/systems/tools/imgtec/simulators
        export IMGTEC_USER_HOME=/projects01/ensigma/systems/tools/imgtec
    else
        export IMGTEC_USER_HOME=~/imgtec
    fi
    echo Simulator directory is $IMGTEC_USER_HOME

    # TODO: Activate Python Virtual Environment
    #  source $PROJ_DIR/imgtec/venvs/cs869/bin/activate
    echo Python used : `which python` version
    echo `python --version`

    # Stack unused arguments skipping the first two already consumed.
    shift 2
    args=
    while [ $# -gt 0 ]; do
        token=$1
        args="${args} ${token}"
        shift
    done

    # Run test script. -B to prevent pyc files.
    cd $SCRIPT_PATH
    echo Python script args =  $args
    python -B PHY_performance.py $args
    rc2=$?
else
    echo Not testing.
    rc2=0
fi

exit 0


# configs
user=vagrant
redis_package=http://download.redis.io/releases/redis-2.8.11.tar.gz

#
sudo apt-get update
sudo apt-get install -y vim git make
sudo apt-get install -y python-pip python-virtualenv

# switch to /vagrant
cd /$user

# setup virtualenv
if [ ! -f venv ]
then
  virtualenv venv 
  source venv/bin/activate
fi

# install requirements.txt
venv/bin/pip install -r requirements.txt

# download / install / configure redis 
if [ ! -f /usr/local/bin/redis-cli ]
then
  temp=`mktemp -d`
  pushd $temp > /dev/null
  wget $redis_package
  tgz=$(basename $redis_package)
  dir=$(echo $tgz | sed 's/\(.tgz\|.tar.gz\)//;')
  tar -xvzf $tgz
  cd $dir
  make
  make install

  # config redis
  # http://redis.io/topics/quickstart
  cd utils
  ./install_server.sh
  popd > /dev/null
  rm -rf $temp
fi


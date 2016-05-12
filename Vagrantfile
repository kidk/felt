#
# Vagrant box for Felt development
# PhantomJS and SlimerJS come preinstalled
#

phantomjs = "phantomjs-2.1.1-linux-x86_64"
slimerjs = "slimerjs-0.10.0"

Vagrant.configure("2") do |config|
    config.vm.box = "ubuntu/trusty64"

    config.vm.provision "apt_update", type: "shell" do |s|
        s.inline = "apt-get update"
    end

    config.vm.provision "install_dependencies_apt", type: "shell" do |s|
        s.inline = "apt-get -y install xvfb firefox unzip python-pip"
    end

    config.vm.provision "install_dependencies_pip", type: "shell" do |s|
        s.inline = "pip install commentjson"
    end

    config.vm.provision "install_phantomjs", type: "shell" do |s|
        s.inline = "wget -nv https://bitbucket.org/ariya/phantomjs/downloads/" + phantomjs + ".tar.bz2 && tar jvxf " + phantomjs + ".tar.bz2 && rm " + phantomjs + ".tar.bz2 && chown -R vagrant:vagrant " + phantomjs
    end

    config.vm.provision "install_slimerjs", type: "shell" do |s|
        s.inline = "wget -nv http://download.slimerjs.org/releases/0.10.0/" + slimerjs + ".zip && unzip " + slimerjs + ".zip && rm " + slimerjs + ".zip && chown -R vagrant:vagrant " + slimerjs
    end

    config.vm.provision "setup_path", type: "shell" do |s|
        s.inline = 'echo PATH="$PATH:/home/vagrant/' + phantomjs + '/bin/:/home/vagrant/' + slimerjs + '/" >> /home/vagrant/.bashrc'
    end

    config.vm.provision "setup_display", type: "shell" do |s|
        s.inline = 'echo DISPLAY=":10" >> /home/vagrant/.bashrc'
    end

    config.vm.provision "start_display", type: "shell", privileged: false do |s|
        s.inline = 'Xvfb :10 &'
    end
end

Vagrant.configure(2) do |config|

  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.cpus = 2
  end

  config.vm.box = "scoop/backend-base"
  config.vm.box_url = "https://vagrant.apps-foundry.com/scoop/backend-base.json"
  config.vm.synced_folder "../db-dumps/", "/var/db-dumps", create: true

end

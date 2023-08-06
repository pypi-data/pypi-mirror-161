------------
secure sedge
------------

``sedge`` is a collection of convocations that are designed
to serve the following purpose(s):

#. allow the keystore instance to request certs
   from letsencrypt and then upload them to ssm parameter store

#. allow individual servers to pull their individual certs from
   ssm parameter store and install them on both linux
   and windows.

#. that's it.

sedge is tightly integrated with aws and makes use of route53 and ssm
parameter store via ``boto3``.

======================
setup and installation
======================

#. make sure you have python 3.8 installed

    #. ubuntu

        .. code-block:: bash

          sudo apt -y update
          sudo add-apt-repository -y ppa:deadsnakes/ppa
          sudo apt -qq update
          sudo apt -y install python3.8 python3.8-dev python3.8-venv

    #. powershell

        .. code-block:: powershell

          choco install -y python3 --version 3.8.4 --params "/installdir:c:\python38"
          $mac = [System.EnvironmentVariableTarget]::Machine
          $path = [system.environment]::getenvironmentvariable('path', $mac)
          $path = "${path};c:\python38;c:\python38\scripts"
          [system.environment]::setenvironmentvariable('path', $path, $mac)

#. install secure_sedge using pip

    .. code-block:: bash

      pip install secure_sedge

#. create one or more config file on your keystore

    .. code-block:: bash

      mkdir -p /etc/sedge
      sudo chown -R sedge:sedge /etc/sedge

   in a file called ```defaults.yml`` we can specify defaults to use for all
   certs.  and then one yaml file per cert that we want sedge to renew.

    .. code-block:: yaml
      :linenos:

      ---
      # the namespaces key will specify all of the namespaces in ssm
      # parameter store that the cert will be saved into
      namespaces:
        - dev
        - staging

      # the name of the profile in aws that we want to use
      profile: ewoks

      # the primary hostname / subject identifier for the cert
      # we can specify a wildcard here, but no ip addresses
      hostname: computer.contoso.com

      # any subject alternative domains that we also want secured by the cert
      # n.b., there can't be overlapping domains like having a wildcard
      # for the hostname and then a specific host.
      alt_domains:
        - computer.fabrikam.com

   certs created by ``renew_all`` will be stored at the following path:
   ``/namespace/apps_keystore/hostname/cert`` and the private key will be
   stored at ``/namespace/apps_keystore/hostname/key``.

#. create one or more config files on your server

   on the system on
   which the cert will be installed, we create another yaml
   config file that looks like below:

    .. code-block:: yaml
      :linenos:

      ---
      namespace: dev
      # should match the *primary* hostname in the requesting config file
      hostname: computer.contoso.com
      # aws / boto3 profile configured (if any) on the server to allow
      # communications to aws
      profile: default

      # the following parameters are linux-only:  certificate, key,
      #   owner, group

      # certificate defaults to /etc/ssl/certs/{{ hostname }}.bundled.crt
      certificate: /etc/ssl/certs/public.crt

      # key defaults to /etc/ssl/private/{{ hostname }}.key
      key: /etc/ssl/private/private.key

      # defaults to root / root
      owner: nginx
      group: nginx

   On windows, the pfx cert will be imported to the ``cert:\localMachine\my``
   cert store.

#. set up a cron job or scheduled task on your keystore to renew certs

      .. code-block:: bash

        /path/to/sedge renew_all -d /path/to/config/dir

#. set up a cron job or scheduled task on your server to pull down the
   cert from ssm at regular intervals and install it

      .. code-block:: bash

        /path/to/sedge install_cert -c /path/to/config/file


System Config of mirrors.ustc.edu.cn
------------------------------------

This repository is created for version control of system-wide configs.

Several configs in /etc/ should be symlinked here.

ln -s nginx /etc/nginx
ln -s rsyncd.conf /etc/rsyncd.conf
ln -s vsftpd.conf /etc/vsftpd.conf

ln -s fstab /etc/fstab			# for FTP bind mounts
ln -s rc.local /etc/rc.local		# init script, routing rules

ln -s logrotate.d /etc/logrotate.d

ln -s ganglia /etc/ganglia
ln -s collectd /etc/collectd

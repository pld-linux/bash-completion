# vim:ft=spec
# TODO
# - bittorrent complete doesn't actually handle our prognames
# - use mkinitrd and update for geninitrd
# - can we have duplicate trigger on pwdutils pkg? merge files?
# - fix vim not to mark this file as bash
Summary:	bash-completion offers programmable completion for bash
Summary(pl.UTF-8):	Programowalne uzupełnianie nazw dla basha
Name:		bash-completion
Version:	1.2
Release:	3
Epoch:		1
License:	GPL
Group:		Applications/Shells
Source0:	http://bash-completion.alioth.debian.org/files/%{name}-%{version}.tar.gz
# Source0-md5:	457c8808ed54f2b2cdd737b1f37ffa24
Source1:	%{name}-poldek.sh
Source2:	%{name}.sh
# https://bugs.launchpad.net/ubuntu/+source/mysql-dfsg-5.0/+bug/106975
Source3:	http://launchpadlibrarian.net/19164189/mysqldump
# Source3-md5:	09e4885be92e032400ed702f39925d85
Source4:	http://svn.php.net/viewvc/pear2/sandbox/PEAR_BashCompletion/trunk/pear?revision=285425&view=co#/pear
# Source4-md5:	8ce77e4459e2c45e2096da8d03c8f43d
Patch0:		%{name}-rpm-cache.patch
URL:		http://bash-completion.alioth.debian.org/
Requires(triggerpostun):	sed >= 4.0
Requires:	bash >= 2.05a-3
Requires:	issue
Obsoletes:	bash-completion-rpm-cache
Conflicts:	rpm < 4.4.9-44
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
bash-completion is a collection of shell functions that take advantage
of the programmable completion feature of bash 2.04 and later.

%description -l pl.UTF-8
bash-completion jest kolekcją funkcji shella, które opierają się na
wbudowanych rozszerzeniach basha 2.04 lub późniejszego umożliwiającego
kompletowanie parametrów linii poleceń.

%prep
%setup -q
%patch0 -p1
cp -a %{SOURCE1} contrib/poldek
cp -a %{SOURCE3} contrib/mysqldump
cp -a %{SOURCE4} contrib/pear

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

# packaged by subversion.spec
rm contrib/_subversion
# soon packaged by yum, but not yet
mv contrib/{_,}yum
mv contrib/{_,}yum-utils

# No package matches '*/apache2ctl'
rm contrib/apache2ctl

# No PLD package or no such binary to complete on
rm contrib/{larch,lisp,_modules,monodevelop,p4,cowsay,cpan2dist}
rm contrib/{cfengine,mkinitrd,rpmcheck}
rm contrib/{kldload,pkg_install,portupgrade,pkgtools} # FreeBSD Stuff
rm contrib/{apt-build,dselect,_mock,reportbug,sysv-rc,update-alternatives,lintian}

# no package to hook to
rm contrib/configure

# split freeciv-client,freeciv-server as we have these in separate packages
mv contrib/freeciv .
%{__sed} -ne '1,2p;/have civserver/,/complete -F _civserver civserver/p;/# Local/,/# ex:/p' freeciv > contrib/freeciv-server
%{__sed} -ne '1,2p;/have civclient/,/complete -F _civclient civclient/p;/# Local/,/# ex:/p' freeciv > contrib/freeciv-client
if [ $(md5sum freeciv | awk '{print $1}') != "7e3549ec737e9eef01305ad941d5e8b6" ]; then
	: check that split out contrib/freeciv-{client,server} are ok and update md5sum
	exit 1
fi

# split munin as we have subpackage for node
mv contrib/munin-node .
%{__sed} -ne '1,2p;/have munin-run/,/complete -F _munin_update/p;/# Local/,/# ex:/p' munin-node > contrib/munin
%{__sed} -ne '1,2p;/have munin-node-configure /,/complete -F _munin_node_configure/p;/# Local/,/# ex:/p' munin-node > contrib/munin-node
if [ $(md5sum munin-node | awk '{print $1}') != "0f7b9278eafe5b822a18c1bc7cc2e026" ]; then
	: check that split out contrib/munin{,-node} are ok and update md5sum
	exit 1
fi

# we have lastlog in sysvinit package
mv contrib/shadow .
%{__sed} -ne '1,/complete -F _faillog faillog/p;/# Local/,/# ex:/p' shadow > contrib/shadow
%{__sed} -ne '1,2p;/have lastlog/,$p' shadow > contrib/sysvinit
if [ $(md5sum shadow | awk '{print $1}') != "1e54016f614554139cb910defceda1f3" ]; then
	: check that split out contrib/{shadow,sysvinit} are ok and update md5sum
	exit 1
fi

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/bash_completion.d,/etc/shrc.d,%{_datadir}/%{name}}

err=0
check_triggers() {
	for comp in $(awk '/^%%bashcomp_trigger/{print $3 ? $3 : $2}' %{_specdir}/%{name}.spec | tr ',' ' '); do
		l=$(awk -vcomp=$comp '$0 == "%%{_datadir}/%%{name}/" comp {print}' %{_specdir}/%{name}.spec)
		if [ -z "$l" ]; then
			echo >&2 "!! $comp not listed in %%files"
			err=1
		fi
	done
	for comp in $(awk -F/ '$0 ~ "^%%{_datadir}/%%{name}/"{print $NF}' %{_specdir}/%{name}.spec); do
		l=$(awk -vcomp=$comp '/^%%bashcomp_trigger/ && ($3 ? $3 : $2) ~ "(^|,)"comp"(,|$)"' %{_specdir}/%{name}.spec)
		if [ -z "$l" ]; then
			echo >&2 "!! $comp has no trigger"
			err=1
		fi
	done
}
check_triggers
[ "$err" != 0 ] && exit $err

cp -a bash_completion $RPM_BUILD_ROOT%{_sysconfdir}
cp -a contrib/* $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -a %{SOURCE2} $RPM_BUILD_ROOT/etc/shrc.d

# Take care of contrib files
for a in contrib/*; do
	f=${a##*/}
	ln -s ../..%{_datadir}/%{name}/$f $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d
	echo "%ghost %{_sysconfdir}/bash_completion.d/$f"
done > %{name}-ghost.list

%clean
rm -rf $RPM_BUILD_ROOT

%triggerpostun -- %{name} < 20050721-3.9
sed -i -e '/^# START bash completion/,/^# END bash completion/d' /etc/bashrc

%triggerpostun -- %{name} < 20081219-0.1
# don't do anything on --downgrade
if [ $1 -le 1 ]; then
	exit 0
fi
# No rpm in vservers
if [ ! -x /bin/rpm ]; then
	exit 0
fi

# This ugly trigger is here because we package same pathnames as ghost
# meaning the files will lay around from previous package version.

# get files which are ghost for us
files=$(rpm -ql %{name}-%{version}-%{release} | grep %{_sysconfdir}/bash_completion.d/)

# this is to get old pkg NVR, actually gives list of files that are
# packaged by other versions than this installed one, which is ok even for
# multiple bash-completion pkgs being installed.
oldpkg=$(rpm -qf $(echo "$files") 2>/dev/null | grep -v 'is not' | sort -u | grep -v %{name}-%{version}-%{release})
for a in $(rpm -ql $oldpkg | grep %{_sysconfdir}/bash_completion.d/); do
	# remove files from old package (which are ghost in new pkg),
	# if not already converted to symlink
	[ -L $a ] || rm -f $a
done

# Usage: bashcomp_trigger PACKAGENAME[,PACKAGENAME] [SCRIPTNAME][,SCRIPTNAME]
%define bashcomp_trigger() \
%triggerin -- %1\
for comp in {%{?2}%{!?2:%1},}; do\
	[ "$comp" ] || continue\
	if [ ! -L %{_sysconfdir}/bash_completion.d/$comp ]; then\
		ln -sf ../..%{_datadir}/%{name}/$comp %{_sysconfdir}/bash_completion.d\
	fi\
done\
%triggerun -- %1\
if [ $2 = 0 ]; then\
	for comp in {%{?2}%{!?2:%1},}; do\
		[ "$comp" ] || continue\
		rm -f %{_sysconfdir}/bash_completion.d/$comp\
	done\
fi
%{nil}

%bashcomp_trigger BitTorrent bittorrent
%bashcomp_trigger ImageMagick imagemagick
%bashcomp_trigger QtDBus qdbus
%bashcomp_trigger X11,xorg-app-xhost xhost
%bashcomp_trigger X11,xorg-app-xrandr xrandr
%bashcomp_trigger abook
%bashcomp_trigger ant
%bashcomp_trigger apt
%bashcomp_trigger aptitude
%bashcomp_trigger aspell
%bashcomp_trigger autorpm
%bashcomp_trigger bash bash-builtins
%bashcomp_trigger bind-utils
%bashcomp_trigger bitkeeper
%bashcomp_trigger bluez
%bashcomp_trigger bridge-utils brctl
%bashcomp_trigger bzip2
%bashcomp_trigger cdrkit,cdrtools wodim
%bashcomp_trigger cdrtools-mkisofs,dvdrtools-mkisofs genisoimage
%bashcomp_trigger chkconfig
%bashcomp_trigger cksfv
%bashcomp_trigger clisp
%bashcomp_trigger coreutils
%bashcomp_trigger coreutils dd
%bashcomp_trigger cpio
%bashcomp_trigger cryptsetup-luks,cryptsetup cryptsetup
%bashcomp_trigger cups-clients cups
%bashcomp_trigger cvsnt,cvs cvs
%bashcomp_trigger cvsps
%bashcomp_trigger dhcp-client dhclient
%bashcomp_trigger dict
%bashcomp_trigger dpkg
%bashcomp_trigger dsniff
%bashcomp_trigger expat xmlwf
%bashcomp_trigger findutils
%bashcomp_trigger freeciv-client
%bashcomp_trigger freeciv-server
%bashcomp_trigger freeswan ipsec
%bashcomp_trigger fuse
%bashcomp_trigger gcc,gcc-java,fortran,gcc-c++ gcc
%bashcomp_trigger gcc-ada gnatmake
%bashcomp_trigger gcl
%bashcomp_trigger gdb
%bashcomp_trigger gkrellm
%bashcomp_trigger glibc iconv
%bashcomp_trigger glibc-misc getent
%bashcomp_trigger gnupg gpg
%bashcomp_trigger gnupg2 gpg2
%bashcomp_trigger gzip
%bashcomp_trigger heimdal
%bashcomp_trigger hping2
%bashcomp_trigger info,pinfo info
%bashcomp_trigger ipmitool
%bashcomp_trigger iptables
%bashcomp_trigger ipv6calc
%bashcomp_trigger jar
%bashcomp_trigger java-sun-jre,java-gcj-compat java
%bashcomp_trigger k3b
%bashcomp_trigger ldapvi
%bashcomp_trigger lftp
%bashcomp_trigger libxml2-progs xmllint
%bashcomp_trigger lilo
%bashcomp_trigger links
%bashcomp_trigger lvm2 lvm
%bashcomp_trigger lzma,xz lzma
%bashcomp_trigger lzop
%bashcomp_trigger mailman
%bashcomp_trigger make
%bashcomp_trigger man
%bashcomp_trigger mc
%bashcomp_trigger mcrypt
%bashcomp_trigger mdadm
%bashcomp_trigger medusa
%bashcomp_trigger minicom
%bashcomp_trigger module-init-tools
%bashcomp_trigger mount
%bashcomp_trigger mplayer
%bashcomp_trigger mtx
%bashcomp_trigger multisync-msynctool,msynctool msynctool
%bashcomp_trigger munin
%bashcomp_trigger munin-node
%bashcomp_trigger mutt
%bashcomp_trigger mysql-client mysqladmin,mysqldump
%bashcomp_trigger ncftp
%bashcomp_trigger net-tools
%bashcomp_trigger nfs-utils rpcdebug
%bashcomp_trigger nmap
%bashcomp_trigger ntp-client ntpdate
%bashcomp_trigger openldap
%bashcomp_trigger openssh-clients ssh
%bashcomp_trigger openssl-tools openssl
%bashcomp_trigger pcmciautils cardctl
%bashcomp_trigger perl-base perl
%bashcomp_trigger php-pear-PEAR pear
%bashcomp_trigger pine
%bashcomp_trigger pkgconfig pkg-config
%bashcomp_trigger pm-utils
%bashcomp_trigger poldek
%bashcomp_trigger postfix
%bashcomp_trigger postgresql-clients postgresql
%bashcomp_trigger povray
%bashcomp_trigger procps
%bashcomp_trigger procps sysctl
%bashcomp_trigger pwdutils shadow
%bashcomp_trigger pwdutils,shadow-extras chsh
%bashcomp_trigger python
%bashcomp_trigger qemu
%bashcomp_trigger quota-tools
%bashcomp_trigger rc-scripts service,ifupdown
%bashcomp_trigger rcs
%bashcomp_trigger rdesktop
%bashcomp_trigger resolvconf
%bashcomp_trigger rfkill
%bashcomp_trigger rpm
%bashcomp_trigger rrdtool
%bashcomp_trigger rsync
%bashcomp_trigger ruby-modules ri
%bashcomp_trigger samba-client samba
%bashcomp_trigger sbcl
%bashcomp_trigger screen
%bashcomp_trigger sitecopy
%bashcomp_trigger smartmontools,smartsuite smartctl
%bashcomp_trigger snownews
%bashcomp_trigger sshfs-fuse sshfs
%bashcomp_trigger strace
%bashcomp_trigger svk
%bashcomp_trigger tar
%bashcomp_trigger tcpdump
%bashcomp_trigger tightvnc vncviewer
%bashcomp_trigger unace
%bashcomp_trigger unixODBC isql
%bashcomp_trigger unrar
%bashcomp_trigger upstart-SysVinit,SysVinit sysvinit
%bashcomp_trigger util-linux,util-linux-ng util-linux
%bashcomp_trigger util-linux-ng rtcwake
%bashcomp_trigger vpnc
%bashcomp_trigger wireless-tools
%bashcomp_trigger wol
%bashcomp_trigger wtf
%bashcomp_trigger wvdial
%bashcomp_trigger xen xm
%bashcomp_trigger xmms
%bashcomp_trigger xsltproc
%bashcomp_trigger xz
%bashcomp_trigger yp-tools
%bashcomp_trigger yum
%bashcomp_trigger yum-arch
%bashcomp_trigger yum-utils

%files -f %{name}-ghost.list
%defattr(644,root,root,755)
%doc README TODO
/etc/shrc.d/%{name}.sh
%{_sysconfdir}/bash_completion
%dir %{_sysconfdir}/bash_completion.d
%dir %{_datadir}/%{name}
# we list all files to be sure we have all of them handled by triggers
%{_datadir}/%{name}/abook
%{_datadir}/%{name}/ant
%{_datadir}/%{name}/apt
%{_datadir}/%{name}/aptitude
%{_datadir}/%{name}/aspell
%{_datadir}/%{name}/autorpm
%{_datadir}/%{name}/bash-builtins
%{_datadir}/%{name}/bind-utils
%{_datadir}/%{name}/bitkeeper
%{_datadir}/%{name}/bittorrent
%{_datadir}/%{name}/bluez
%{_datadir}/%{name}/brctl
%{_datadir}/%{name}/bzip2
%{_datadir}/%{name}/cardctl
%{_datadir}/%{name}/chkconfig
%{_datadir}/%{name}/chsh
%{_datadir}/%{name}/cksfv
%{_datadir}/%{name}/clisp
%{_datadir}/%{name}/coreutils
%{_datadir}/%{name}/cpio
%{_datadir}/%{name}/cryptsetup
%{_datadir}/%{name}/cups
%{_datadir}/%{name}/cvs
%{_datadir}/%{name}/cvsps
%{_datadir}/%{name}/dd
%{_datadir}/%{name}/dhclient
%{_datadir}/%{name}/dict
%{_datadir}/%{name}/dpkg
%{_datadir}/%{name}/dsniff
%{_datadir}/%{name}/findutils
%{_datadir}/%{name}/freeciv-client
%{_datadir}/%{name}/freeciv-server
%{_datadir}/%{name}/fuse
%{_datadir}/%{name}/gcc
%{_datadir}/%{name}/gcl
%{_datadir}/%{name}/gdb
%{_datadir}/%{name}/genisoimage
%{_datadir}/%{name}/getent
%{_datadir}/%{name}/gkrellm
%{_datadir}/%{name}/gnatmake
%{_datadir}/%{name}/gpg
%{_datadir}/%{name}/gpg2
%{_datadir}/%{name}/gzip
%{_datadir}/%{name}/heimdal
%{_datadir}/%{name}/hping2
%{_datadir}/%{name}/iconv
%{_datadir}/%{name}/ifupdown
%{_datadir}/%{name}/imagemagick
%{_datadir}/%{name}/info
%{_datadir}/%{name}/ipmitool
%{_datadir}/%{name}/ipsec
%{_datadir}/%{name}/iptables
%{_datadir}/%{name}/ipv6calc
%{_datadir}/%{name}/isql
%{_datadir}/%{name}/jar
%{_datadir}/%{name}/java
%{_datadir}/%{name}/k3b
%{_datadir}/%{name}/ldapvi
%{_datadir}/%{name}/lftp
%{_datadir}/%{name}/lilo
%{_datadir}/%{name}/links
%{_datadir}/%{name}/lvm
%{_datadir}/%{name}/lzma
%{_datadir}/%{name}/lzop
%{_datadir}/%{name}/mailman
%{_datadir}/%{name}/make
%{_datadir}/%{name}/man
%{_datadir}/%{name}/mc
%{_datadir}/%{name}/mcrypt
%{_datadir}/%{name}/mdadm
%{_datadir}/%{name}/medusa
%{_datadir}/%{name}/minicom
%{_datadir}/%{name}/module-init-tools
%{_datadir}/%{name}/mount
%{_datadir}/%{name}/mplayer
%{_datadir}/%{name}/msynctool
%{_datadir}/%{name}/mtx
%{_datadir}/%{name}/munin
%{_datadir}/%{name}/munin-node
%{_datadir}/%{name}/mutt
%{_datadir}/%{name}/mysqladmin
%{_datadir}/%{name}/mysqldump
%{_datadir}/%{name}/ncftp
%{_datadir}/%{name}/net-tools
%{_datadir}/%{name}/nmap
%{_datadir}/%{name}/ntpdate
%{_datadir}/%{name}/openldap
%{_datadir}/%{name}/openssl
%{_datadir}/%{name}/pear
%{_datadir}/%{name}/perl
%{_datadir}/%{name}/pine
%{_datadir}/%{name}/pkg-config
%{_datadir}/%{name}/pm-utils
%{_datadir}/%{name}/poldek
%{_datadir}/%{name}/postfix
%{_datadir}/%{name}/postgresql
%{_datadir}/%{name}/povray
%{_datadir}/%{name}/procps
%{_datadir}/%{name}/python
%{_datadir}/%{name}/qdbus
%{_datadir}/%{name}/qemu
%{_datadir}/%{name}/quota-tools
%{_datadir}/%{name}/rcs
%{_datadir}/%{name}/rdesktop
%{_datadir}/%{name}/resolvconf
%{_datadir}/%{name}/rfkill
%{_datadir}/%{name}/ri
%{_datadir}/%{name}/rpcdebug
%{_datadir}/%{name}/rpm
%{_datadir}/%{name}/rrdtool
%{_datadir}/%{name}/rsync
%{_datadir}/%{name}/rtcwake
%{_datadir}/%{name}/samba
%{_datadir}/%{name}/sbcl
%{_datadir}/%{name}/screen
%{_datadir}/%{name}/service
%{_datadir}/%{name}/shadow
%{_datadir}/%{name}/sitecopy
%{_datadir}/%{name}/smartctl
%{_datadir}/%{name}/snownews
%{_datadir}/%{name}/ssh
%{_datadir}/%{name}/sshfs
%{_datadir}/%{name}/strace
%{_datadir}/%{name}/svk
%{_datadir}/%{name}/sysctl
%{_datadir}/%{name}/sysvinit
%{_datadir}/%{name}/tar
%{_datadir}/%{name}/tcpdump
%{_datadir}/%{name}/unace
%{_datadir}/%{name}/unrar
%{_datadir}/%{name}/util-linux
%{_datadir}/%{name}/vncviewer
%{_datadir}/%{name}/vpnc
%{_datadir}/%{name}/wireless-tools
%{_datadir}/%{name}/wodim
%{_datadir}/%{name}/wol
%{_datadir}/%{name}/wtf
%{_datadir}/%{name}/wvdial
%{_datadir}/%{name}/xhost
%{_datadir}/%{name}/xm
%{_datadir}/%{name}/xmllint
%{_datadir}/%{name}/xmlwf
%{_datadir}/%{name}/xmms
%{_datadir}/%{name}/xrandr
%{_datadir}/%{name}/xsltproc
%{_datadir}/%{name}/xz
%{_datadir}/%{name}/yp-tools
%{_datadir}/%{name}/yum
%{_datadir}/%{name}/yum-arch
%{_datadir}/%{name}/yum-utils

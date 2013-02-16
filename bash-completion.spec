# vim:ft=spec
# TODO
# - use mkinitrd and update for geninitrd
# - fix vim not to mark this file as bash
Summary:	bash-completion offers programmable completion for bash
Summary(pl.UTF-8):	Programowalne uzupełnianie nazw dla basha
Name:		bash-completion
Version:	2.0
Release:	3
Epoch:		1
License:	GPL v2+
Group:		Applications/Shells
Source0:	http://bash-completion.alioth.debian.org/files/%{name}-%{version}.tar.bz2
# Source0-md5:	0d903f398be8c8f24bc5ffa6f86127f8
Source1:	%{name}-poldek.sh
# https://bugs.launchpad.net/ubuntu/+source/mysql-dfsg-5.0/+bug/106975
Source3:	http://launchpadlibrarian.net/19164189/mysqldump
# Source3-md5:	09e4885be92e032400ed702f39925d85
Source4:	http://svn.php.net/viewvc/pear2/sandbox/PEAR_BashCompletion/trunk/pear?revision=285425&view=co#/pear
# Source4-md5:	8ce77e4459e2c45e2096da8d03c8f43d
Patch0:		%{name}-rpm-cache.patch
Patch1:		pear.patch
URL:		http://bash-completion.alioth.debian.org/
BuildRequires:	sed >= 4.0
Requires(triggerpostun):	sed >= 4.0
Requires:	bash >= 4.1
Requires:	issue
Obsoletes:	bash-completion-rpm-cache
Conflicts:	rpm < 4.4.9-44
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
bash-completion is a collection of shell functions that take advantage
of the programmable completion feature of bash 4.1 and later.

%description -l pl.UTF-8
bash-completion jest kolekcją funkcji shella, które opierają się na
wbudowanych rozszerzeniach basha 4.1 lub późniejszego umożliwiającego
dopełnianie parametrów linii poleceń.

%prep
%setup -q
cp -p '%{SOURCE4}' completions/pear
%patch0 -p1
%patch1 -p1

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' ')' -print0 | xargs -0 -r -l512 rm -f

# update path
%{__sed} -i -e 's#${BASH_SOURCE\[0\]%/\*}#%{_datadir}/%{name}#' completions/perl

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d

%{__make} install -j1 \
	INSTALL="install -p" \
	profiledir=/etc/shrc.d \
	DESTDIR=$RPM_BUILD_ROOT

cp -p completions/_yum $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/yum
cp -p completions/_yum-utils $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/yum-utils

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/poldek
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/mysqldump
cp -p completions/pear $RPM_BUILD_ROOT%{_datadir}/%{name}/completions

# No package matches '*/apache2ctl'
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/apache2ctl
# No PLD package or no such binary to complete on
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/{larch,lisp,monodevelop,[pg]4,cowsay,cowthink,cpan2dist}
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/{mkinitrd,rpmcheck}
# FreeBSD stuff
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/{kldload,portupgrade}
# Debian stuff
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/completions/{apt-build,dselect,reportbug,alternatives,update-alternatives,lintian,lintian-info}


# do not generate autodeps
chmod a-x $RPM_BUILD_ROOT%{_datadir}/%{name}/helpers/perl

%clean
rm -rf $RPM_BUILD_ROOT

%triggerpostun -- %{name} < 20050721-3.9
sed -i -e '/^# START bash completion/,/^# END bash completion/d' /etc/bashrc

%files
%defattr(644,root,root,755)
%doc AUTHORS CHANGES README
/etc/shrc.d/bash_completion.sh
%dir %{_sysconfdir}/bash_completion.d
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/bash_completion
%dir %{_datadir}/%{name}/completions
%{_datadir}/%{name}/completions/*
%dir %{_datadir}/%{name}/helpers
%attr(755,root,root) %{_datadir}/%{name}/helpers/perl
%{_npkgconfigdir}/bash-completion.pc

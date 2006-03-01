Summary:	bash-completion offers programmable completion for bash
Summary(pl):	Programowalne uzupe³nianie nazw dla basha
Name:		bash-completion
Version:	20060301
Release:	1
License:	GPL
Group:		Applications/Shells
Source0:	http://www.caliban.org/files/bash/%{name}-%{version}.tar.bz2
# Source0-md5:	ed95a89f57357a42b8e4eb95487bf9d0
Source1:	%{name}-poldek.sh
Patch0:		%{name}-FHS.patch
Patch1:		%{name}-rpm-arch.patch
URL:		http://www.caliban.org/bash/
Requires(triggerpostun):	sed >= 4.0
Requires:	bash >= 2.05a-3
Obsoletes:	bash-completion-rpm-cache
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
bash-completion is a collection of shell functions that take advantage
of the programmable completion feature of bash 2.04 and later.

%description -l pl
bash-completion jest kolekcj± funkcji shella, które opieraj± siê na
wbudowanych rozszerzeniach basha 2.04 lub pó¼niejszego umo¿liwiaj±cego
kompletowanie parametrów linii poleceñ.

%prep
%setup -q -n bash_completion
%patch0 -p1
%patch1 -p1

cat <<'EOF' > %{name}.sh
# check for bash
[ -z "$BASH_VERSION" ] && return

# must be interactive shell, not script
[[ $- = *i* ]] || return

# check for correct version of bash
bash=${BASH_VERSION%%.*}; bmajor=${bash%%.*}; bminor=${bash#*.}
if [ "$bmajor" -eq 2 -a "$bminor" '>' 04 ] || [ "$bmajor" -gt 2 ]; then
	if [ "$PS1" ]; then # interactive shell
		# Source completion code
		. %{_sysconfdir}/bash_completion
	fi
fi
unset bash bminor bmajor
EOF

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/bash_completion.d,/etc/shrc.d,/var/cache}

install bash_completion $RPM_BUILD_ROOT%{_sysconfdir}
install contrib/*	$RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d
> $RPM_BUILD_ROOT/var/cache/rpmpkgs.txt
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/poldek
install %{name}.sh $RPM_BUILD_ROOT/etc/shrc.d

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f /var/cache/rpmpkgs.txt ]; then
	touch /var/cache/rpmpkgs.txt
	chown root:wheel /var/cache/rpmpkgs.txt
	chmod 664 /var/cache/rpmpkgs.txt

	# rpm binary check for vservers
	if [ -x /bin/rpm ]; then
		export LC_ALL=C
		rpm -qa --qf '%%{name}-%%{version}-%%{release}.%%{arch}.rpm\n' 2>&1 | sort > /var/cache/rpmpkgs.txt
	fi
fi

%triggerpostun -- %{name} < 20050721-3.9
sed -i -e '/^# START bash completion/,/^# END bash completion/d' /etc/bashrc
chown root:wheel /var/cache/rpmpkgs.txt
chmod 664 /var/cache/rpmpkgs.txt

%files
%defattr(644,root,root,755)
%doc README Changelog BUGS
%{_sysconfdir}/bash_completion
%{_sysconfdir}/bash_completion.d
%attr(755,root,root) /etc/shrc.d/%{name}.sh
%ghost %attr(664,root,wheel) /var/cache/rpmpkgs.txt

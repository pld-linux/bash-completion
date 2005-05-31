Summary:	bash-completion offers programmable completion for bash
Summary(pl):	Programowalne uzupe³nianie nazw dla basha
Name:		bash-completion
Version:	20050121
Release:	3
License:	GPL
Group:		Applications/Shells
Source0:	http://www.caliban.org/files/bash/%{name}-%{version}.tar.bz2
# Source0-md5:	fafeed562b01a8dee079eb851579f2d2
Source1:	%{name}.cron
Patch0:		%{name}-FHS.patch
Patch1:		%{name}-ifcfg.patch
URL:		http://www.caliban.org/bash/
Requires(triggerpostun):	sed >= 4.0
BuildArch:	noarch
Requires:	bash >= 2.05a-3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
bash-completion is a collection of shell functions that take advantage
of the programmable completion feature of bash 2.04 and later.

%description -l pl
bash-completion jest kolekcj± funkcji shella, które opieraj± siê na
wbudowanych rozszerzeniach basha 2.04 lub pó¼niejszego umo¿liwiaj±cego
kompletowanie parametrów linii poleceñ.

%package rpm-cache
Summary:	Cache result of rpm -qa
Summary(pl):	Buforowanie wyniku rpm -qa
Group:		Applications/Shells

%description rpm-cache
This package contains cached version of rpm -qa, which is used for rpm
completion for faster completion.

%description rpm-cache -l pl
Ten pakiet zawiera skrypt buforuj±cy wynik rpm -qa w celu szybszego
dope³niania linii poleceñ programu rpm.

%prep
%setup -q -n bash_completion
%patch0 -p1
%patch1 -p2

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/bash_completion.d,/etc/cron.daily,/etc/shrc.d,/var/cache}

install bash_completion $RPM_BUILD_ROOT%{_sysconfdir}
install contrib/*	$RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d

install %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.daily/rpmpkgs
> $RPM_BUILD_ROOT/var/cache/rpmpkgs.txt

# subversion comes with much better completion file
rm $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/subversion

cat <<'EOF' > %{name}.sh
# check for bash
[ -z "$BASH_VERSION" ] && return

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

install %{name}.sh $RPM_BUILD_ROOT/etc/shrc.d

%clean
rm -rf $RPM_BUILD_ROOT

%triggerpostun -- %{name} < 20050112-1
# legacy clean-up
sed -i -e '/^# START bash completion/,/^# END bash completion/d' /etc/bashrc

%files
%defattr(644,root,root,755)
%doc README Changelog BUGS
%{_sysconfdir}/bash_completion
%{_sysconfdir}/bash_completion.d/
%attr(755,root,root) /etc/shrc.d/%{name}.sh

%files rpm-cache
%defattr(644,root,root,755)
%attr(755,root,root) /etc/cron.daily/*
%ghost /var/cache/rpmpkgs.txt

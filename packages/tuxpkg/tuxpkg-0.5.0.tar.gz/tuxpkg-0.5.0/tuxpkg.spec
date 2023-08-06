Name:      tuxpkg
Version:   0.5.0
Release:   0%{?dist}
Summary:   release automation tool for Python projects
License:   Expat
URL:       https://gitlab.com/terceiro/tuxpkg
Source0:   %{pypi_source}


BuildRequires: git
BuildRequires: make
BuildRequires: python3-devel
BuildRequires: python3-flit
BuildRequires: python3-jinja2
BuildRequires: python3-pip
BuildRequires: python3-pytest
BuildRequires: python3-pytest-cov
BuildRequires: python3-pytest-mock

BuildArch: noarch

Requires: python3 >= 3.6
Requires: python3-jinja2

%global debug_package %{nil}

%description
tuxpkg is a command line tool that automates common tasks for releasing Python
projects, including but not limited to building and publishing PIP, Debian,
and RPM packages.

%prep
%setup -q

%build
export FLIT_NO_NETWORK=1
make run
#make man
#make bash_completion

%check
python3 -m pytest test/

%install
mkdir -p %{buildroot}/usr/share/%{name}/
cp -r run %{name} %{buildroot}/usr/share/%{name}/
mkdir -p %{buildroot}/usr/bin
ln -sf ../share/%{name}/run %{buildroot}/usr/bin/%{name}
#mkdir -p %{buildroot}%{_mandir}/man1
#install -m 644 %{name}.1 %{buildroot}%{_mandir}/man1/
#mkdir -p %{buildroot}/usr/share/bash-completion/completions/
#install -m 644 bash_completion/%{name} %{buildroot}/usr/share/bash-completion/completions/

%files
/usr/share/%{name}
%{_bindir}/%{name}
#%{_mandir}/man1/%{name}.1*
#/usr/share/bash-completion/completions/%{name}

%doc README.md
%license LICENSE

%changelog

* Tue Oct 05 2021 Antonio Terceiro <antonio.terceiro@linaro.org> - 0.0.1-1
- Initial version of the package


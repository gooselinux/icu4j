# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# If you want to build with eclipse support
# give rpmbuild option '--with eclipse'

%ifarch %{ix86} x86_64
%define with_eclipse 1
%define without_eclipse 0
%else
%define with_eclipse 0
%define without_eclipse 1
%endif

#%%define with_eclipse %{?_with_eclipse:1}%{!?_with_eclipse:0}
#%%define without_eclipse %{!?_with_eclipse:1}%{?_with_eclipse:0}

%define section free

%define eclipse_base            %{_libdir}/eclipse
# Note:  this next section looks weird having an arch specified in a
# noarch specfile but the parts of the build
# All arches line up between Eclipse and Linux kernel names except i386 -> x86
%ifarch %{ix86}
%define eclipse_arch    x86
%else
%define eclipse_arch   %{_arch}
%endif

Name:           icu4j
Version:        4.0.1
Release:        3.3%{?dist}
Epoch:          1
Summary:        International Components for Unicode for Java
License:        MIT and EPL 
URL:            http://www-306.ibm.com/software/globalization/icu/index.jsp
Group:          Development/Libraries
Source0:        http://download.icu-project.org/files/icu4j/4.0.1/icu4j-4_0_1-src.jar
Patch0:         %{name}-crosslink.patch
# PDE Build is in a location the upstream build.xml doesn't check
Patch4:         %{name}-pdebuildlocation.patch
BuildRequires:  ant
# FIXME:  is this necessary or is it just adding strings in the hrefs in
# the docs?
BuildRequires:  java-javadoc >= 1:1.6.0
# This is to ensure we get OpenJDK and not GCJ
BuildRequires:  java-devel >= 1:1.6.0
BuildRequires:  jpackage-utils >= 0:1.5
Requires:       jpackage-utils
# This is to ensure we get OpenJDK and not GCJ
Requires:       java >= 1:1.6.0
%if %{with_eclipse}
BuildRequires:  eclipse-pde >= 0:3.2.1
%endif
%define         debug_package %{nil}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
The International Components for Unicode (ICU) library provides robust and
full-featured Unicode services on a wide variety of platforms. ICU supports
the most current version of the Unicode standard, and provides support for
supplementary characters (needed for GB 18030 repertoire support).

Java provides a very strong foundation for global programs, and IBM and the
ICU team played a key role in providing globalization technology into Sun's
Java. But because of its long release schedule, Java cannot always keep
up-to-date with evolving standards. The ICU team continues to extend Java's
Unicode and internationalization support, focusing on improving
performance, keeping current with the Unicode standard, and providing
richer APIs, while remaining as compatible as possible with the original
Java text and internationalization API design.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Documentation
Requires:       jpackage-utils
Requires:       java-javadoc >= 1:1.6.0

%description javadoc
Javadoc for %{name}.

%if %{with_eclipse}
%package eclipse
Summary:        Eclipse plugin for %{name}
Group:          Development/Tools
Requires:       jpackage-utils

%description eclipse
Eclipse plugin support for %{name}.

%endif

%prep
%setup -q -c
%patch0 -p0
%patch4 -p0

%{__sed} -i 's/\r//' license.html
%{__sed} -i 's/\r//' APIChangeReport.html
%{__sed} -i 's/\r//' readme.html

sed --in-place "s/ .*bootclasspath=.*//g" build.xml
sed --in-place "s/<date datetime=.*when=\"after\"\/>//" build.xml
sed --in-place "/javac1.3/d" build.xml
sed --in-place "s:/usr/lib:%{_libdir}:g" build.xml

%build
%if %{without_eclipse}
%ant -Dicu4j.javac.source=1.5 -Dicu4j.javac.target=1.5 -Dj2se.apidoc=%{_javadocdir}/java jar docs
%else
%ant -Dj2se.apidoc=%{_javadocdir}/java -Declipse.home=%{eclipse_base} \
  -Declipse.basews=gtk -Declipse.baseos=linux \
  -Declipse.basearch=%{eclipse_arch} \
  -Dicu4j.eclipse.build.version.string=4.0.1.v20090415 \
  jar docs eclipsePDEBuild
%endif

%install
%__rm -rf %{buildroot} 

# jars
%__mkdir_p %{buildroot}%{_javadir}
%__cp -ap %{name}.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}.jar; do %__ln_s ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

# javadoc
%__mkdir_p %{buildroot}%{_javadocdir}/%{name}-%{version}
%__cp -pr doc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%__ln_s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%if %{with_eclipse}
# eclipse
install -d -m755 %{buildroot}/%{eclipse_base}

unzip -qq -d %{buildroot}/%{eclipse_base} eclipseProjects/ICU4J.com.ibm.icu/com.ibm.icu-com.ibm.icu.zip
%endif

%clean
%__rm -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
%doc license.html readme.html APIChangeReport.html
%{_javadir}/%{name}*.jar

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/*

%if %{with_eclipse}
%files eclipse
%defattr(0644,root,root,0755)
%dir %{_libdir}/eclipse
%dir %{_libdir}/eclipse/features
%dir %{_libdir}/eclipse/plugins
%{_libdir}/eclipse/features/*
%{_libdir}/eclipse/plugins/*
%doc license.html readme.html
%endif

%changelog
* Mon Jan 18 2010 Andrew Overholt <overholt@redhat.com> - 1:4.0.1-3.3
- Fix Group tags
- Remove macro in changelog
- Remove unused patches

* Tue Dec  1 2009 Dennis Gregorovic <dgregor@redhat.com> - 1:4.0.1-3.2
- Can't be noarch since we have arch-specific packages

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 1:4.0.1-3.1
- Only build icu4j-eclipse on x86 and x86_64

* Mon Aug 10 2009 Alexander Kurtakov <akurtako@redhat.com> 1:4.0.1-3
- Update qualifier to the Eclipse 3.5.0 release.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:4.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Apr 8 2009 Alexander Kurtakov <akurtako@redhat.com> 1:4.0.1-1
- Update to 4.0.1.

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:3.8.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Oct  8 2008 Ville Skyttä <ville.skytta at iki.fi> - 0:3.8.1-4
- Disable debuginfo package when built with Eclipse support, change to
  noarch when built without it (#464017).

* Mon Aug 11 2008 Andrew Overholt <overholt@redhat.com> 3.8.1-3
- Get rid of eclipse_name macro
- Rebuild with Eclipse 3.4 and put into Eclipse stuff into
  %%{_libdir}/eclipse
- Remove now-unnecessary OSGi configuration dir patch
- Add patch to point to PDE Build location

* Fri Jul 11 2008 Andrew Overholt <overholt@redhat.com> 0:3.8.1-2
- Remove GCJ support due to
  com.sun.tools.doclets.internal.toolkit.taglets.* import (not in gjdoc)

* Fri Jul 11 2008 Andrew Overholt <overholt@redhat.com> 0:3.8.1-1
- 3.8.1

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:3.6.1-3
- drop repotag
- fix license tag

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:3.6.1-2jpp.6
- Autorebuild for GCC 4.3

* Tue Nov 13 2007 Andrew Overholt <overholt@redhat.com> 3.6.1-1jpp.6
- Bump release and change updatetimestamp patch to have DOS
  line-endings.

* Tue Nov 13 2007 Andrew Overholt <overholt@redhat.com> 3.6.1-1jpp.5
- Bump release.

* Fri Sep 28 2007 Andrew Overholt <overholt@redhat.com> 3.6.1-1jpp.4
- Update timestamp to match Eclipse 3.3.1 release.

* Wed Aug 29 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 3.6.1-1jpp.3
- Rebuild for selinux ppc32 issue.

* Wed Jun 27 2007 Ben Konrath <bkonrath@redhat.com> - 0:3.6.1-1jpp.2
- Remove requires eclipse-rcp in eclipse sub-package.

* Thu Jun 07 2007 Ben Konrath <bkonrath@redhat.com> - 0:3.6.1-1jpp.1
- 3.6.1.
- Enable eclipse sub-package.

* Fri Mar 16 2007 Jeff Johnston <jjohnstn@redhat.com> - 0:3.4.5-2jpp.2
- Disable eclipse plugin support temporarily until build problems
  can be worked out.  Plugin is still being built as part of
  eclipse platform.
- BuildRequire sinjdoc.

* Mon Feb 12 2007 Matt Wringe <mwringe@redhat.com> - 0:3.4.5-2jpp.1
- Fix some rpmlint issues
- Make use of buildroot more consistent
- Remove javadoc post and postun sections as per new jpp standard
- Change license section to 'MIT style' license from 'MIT' license.
  This was done since the source package calls the license the 
  "X license" (see readme.html in src jar).
- Install eclipse plugin into /usr/share/eclipse

* Mon Jan 22 2007 Fernando Nasser <fnasser@redhat.com> - 0:3.4.5-2jpp.1
- Merge with upstream

* Mon Jan 22 2007 Fernando Nasser <fnasser@redhat.com> - 0:3.4.5-2jpp
- Add optional eclipse subpackage, created by
  Jeff Johnston  <jjohnstn@rdhat.com> :
- Add eclipse sub-package to create plugins.

* Mon Jan 22 2007 Fernando Nasser <fnasser@redhat.com> - 0:3.4.5-1jpp
- Upgrade to 3.4.5 with merge
- Re-enable javadoc

* Mon Sep 04 2006 Ben Konrath <bkonrath@redhat.com> 0:3.4.5-1jpp_1fc
- 3.4.5.
- Add GCJ support with spec-convert-gcj-1.6.

* Mon Jul 17 2006 Ben Konrath <bkonrath@redhat.com> 0:3.4.4-1jpp_1fc
- 3.4.4.
- Add disable javadocs patch.

* Tue Feb 28 2006 Fernando Nasser <fnasser@redhat.com> - 0:3.2-2jpp_1rh
- First Red Hat build

* Mon Feb 27 2006 Fernando Nasser <fnasser@redhat.com> - 0:3.2-2jpp
- First JPP 1.7 build

* Sun Jan 29 2005 David Walluck <david@jpackage.org> 0:3.2-1jpp
- release (contributed by Mary Ellen Foster <mefoster at gmail.com>)

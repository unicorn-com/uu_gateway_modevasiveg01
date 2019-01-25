#!/bin/sh
rpmbuild --define 'dist .keklabs' --define "_topdir `pwd`" -ba SPECS/mod_evasive.spec

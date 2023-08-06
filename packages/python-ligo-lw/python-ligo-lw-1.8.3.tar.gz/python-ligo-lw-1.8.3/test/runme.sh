#!/bin/sh

BASE="ligolw_sqlite_test"

xmlcanonicalize () {
	for filename in "$@" ; do
		xmllint --c14n "${filename}" >"${filename}"~ && mv -f "${filename}"~ "${filename}" || return;
	done
}

#
# do ligolw_add and ligolw_sqlite produce identical output when used to
# merge two .xml files into a single .xml document?  confirm that URLs can
# be used to identify local source files
#

echo
echo "ligolw_sqlite test 2:  merge .xml.gz files and compare to ligolw_add"
echo "--------------------------------------------------------------------"
rm -vf ${BASE}_ref.xml ${BASE}.sqlite ${BASE}_output.xml
ligolw_add --verbose --output ${BASE}_ref.xml ${BASE}_input.xml.gz ${BASE}_input.xml.gz
ligolw_sqlite --verbose --replace --database ${BASE}.sqlite --extract ${BASE}_output.xml file://${PWD}/${BASE}_input.xml.gz ${BASE}_input.xml.gz
xmlcanonicalize ${BASE}_ref.xml ${BASE}_output.xml || exit
cmp ${BASE}_ref.xml ${BASE}_output.xml || exit
rm -vf ${BASE}.sqlite ${BASE}_output.xml
echo
echo "ligolw_sqlite test 2:  success"
echo "ligolw_add and ligolw_sqlite produced identical merged documents"

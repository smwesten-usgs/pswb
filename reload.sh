#!/bin/bash

#./cleanup.sh

rm *.tar
cp /usr/local/bin/swb2 swb2
cp /usr/local/bin/cdo cdo
tar cvf swbfiles.tar create*.sh write*.sh list*.sh get*.sh *.txt swb2 cdo
./cleanup.sh
condor_rm --all

echo "New tarfile created; ready for new Condor run."

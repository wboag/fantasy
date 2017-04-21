for p in $(ls ../data/2016/raw) ; do
    echo $p
    python player.py $p
    #if [[ $? != 0 ]] ; then
    #    exit
    #fi
done

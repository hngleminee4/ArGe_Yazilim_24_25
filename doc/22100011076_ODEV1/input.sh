ls > y
cat < y | sort | uniq | wc > y1
cat y1
ls | sort | > y2 &
cat < y1 | sort | wc > y3
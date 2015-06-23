# get trang.jar from https://code.google.com/p/jing-trang/downloads/list 

TRANG=java -jar trang.jar

all: content.rng
	echo Done

clean:
	rm -f *.rng

%.rng: %.rnc
	$(TRANG) -I rnc -O rng $^ $@


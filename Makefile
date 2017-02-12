all:
	# set empty database files
	mv vuln.db.empty vuln.db
	# TODO more
	# TODO install necessary modules


clean:
	find . -name \*.pyc -type f -delete
	find . -name .*.swp -type f -delete

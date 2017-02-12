all:
    
    # set empty database files
    for db in 'analysis' 'checksum' 'dict' 'module' 'vuln'; do \
    cp -i "$$db.db.empty" "$$db.db"; \
    done
    
    # TODO more
    # TODO install necessary modules
    #pip3 install shutil


clean:
    find . -name \*.pyc -type f -delete
    find . -name .*.swp -type f -delete

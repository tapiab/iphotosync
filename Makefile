clean:
	python3 setup.py clean

build: clean
	python3 setup.py build bdist_wheel

install: build
	sudo pip uninstall -y  iPhonePhotoSync && sudo pip install dist/*.whl



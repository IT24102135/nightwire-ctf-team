FROM ctfd/ctfd:latest
RUN sed -i 's/^from CTFd.plugins import init_plugins/# from CTFd.plugins import init_plugins/' /opt/CTFd/CTFd/__init__.py && sed -i 's/^init_plugins(app)/# init_plugins(app)/' /opt/CTFd/CTFd/__init__.py
RUN grep -n "init_plugins" /opt/CTFd/CTFd/__init__.py || echo "Patch successful"

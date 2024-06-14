#!/bin/bash
if [ "$1" == "uninstall" ]; then
    rm /usr/local/bin/virt-viewer-launcher
else
    cp virt-viewer-launcher.py /usr/local/bin/virt-viewer-launcher
    chmod 755 /usr/local/bin/virt-viewer-launcher
fi


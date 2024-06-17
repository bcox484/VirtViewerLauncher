#!/usr/bin/env python3
import os
import subprocess
import gi
import signal
from sys import stderr

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def is_running(label):
    state = False
    # 'virsh list' only shows running vms
    file = subprocess.Popen(
        ["virsh", "list"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    virshcmd, _ = file.communicate()
    virshcmd = virshcmd.splitlines()

    # checks line by line for prescence of vm name in command output
    for line in virshcmd:
        if label in line:
            state = True

    return state


def child_cleanup(signum, frame):
    """Get rid of zombie process if virt-viewer exits before script exits"""
    while True:
        try:
            # Prevent parent process from hanging with WNOHANG
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
            elif pid == -1:
                print("Error while waiting for child process", file=stderr)
                break
            else:
                print("Child process %d exited with status %d" % (pid, status))
        except ChildProcessError:
            break


def virt_viewer_window(label):
    """fork and exec virt-viewer window, so the window is not attached to
    the launcher
    """
    proc = subprocess.Popen(["virt-viewer", "--attach", label])
    signal.signal(signal.SIGCHLD, child_cleanup)


def start_vm(button, label):
    if not is_running(label):
        state = subprocess.run(["virsh", "start", label])

        if state.returncode == 0:
            virt_viewer_window(label)
        else:
            print("start_vm() unable to start %s" % label, file=stderr)

        return state.returncode

    else:
        virt_viewer_window(label)
        return 0


def create_buttons(box):
    file = subprocess.Popen(
        ["virsh", "list", "--all"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    virtual_machines, _ = file.communicate()
    virtual_machines = virtual_machines.splitlines()

    vms = [vm.split() for vm in virtual_machines]

    # Remove garbage from output
    vms.remove(vms[0])
    vms.remove(vms[0])
    vms.remove(vms[-1])

    for vm in vms:
        label = vm[1]
        button = Gtk.Button(label=label)
        button.set_vexpand(True)
        button.set_vexpand_set(True)

        button.set_margin_end(1)
        button.set_margin_top(1)
        button.set_margin_bottom(1)
        button.set_margin_start(1)

        button.connect("clicked", start_vm, label)
        box.append(button)


def on_activate(app):
    win = Gtk.ApplicationWindow(application=app)
    scr = Gtk.ScrolledWindow()
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

    win.set_child(scr)
    scr.set_child(box)
    create_buttons(box)

    win.set_default_size(200, 200)
    win.set_title("Virtual Machines")
    win.present()


def main():
    app = Gtk.Application(application_id="vm.interface")
    app.connect("activate", on_activate)
    app.run(None)


if __name__ == "__main__":
    main()

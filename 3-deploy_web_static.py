#!/usr/bin/python3
"""
Fabric script that creates and distributes an archive to web servers using the function deploy.
"""

from fabric.api import local
from datetime import datetime
from os.path import exists
from fabric.operations import put, run
from fabric.api import env
from fabric.context_managers import cd

# Set the environment variables
env.user = 'ubuntu'  # Update with your username
env.hosts = ['34.232.52.252, 18.233.64.118']  # Update with your server IPs

def do_pack():
    """
    Generates a .tgz archive from the contents of the web_static folder.

    Returns:
        Archive path if successful, None otherwise.
    """
    # Create the 'versions' folder if it doesn't exist
    local("mkdir -p versions")

    # Get the current date and time
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")

    # Set the archive path
    archive_path = "versions/web_static_{}.tgz".format(timestamp)

    # Create the .tgz archive
    result = local("tar -cvzf {} web_static".format(archive_path))

    # Check if the archive was created successfully
    if result.failed:
        return None
    else:
        return archive_path

def do_deploy(archive_path):
    """
    Distributes an archive to web servers.

    Args:
        archive_path: Path to the archive to be deployed.

    Returns:
        True if all operations are done correctly, False otherwise.
    """
    if not exists(archive_path):
        return False

    # Get the filename without extension
    filename = os.path.basename(archive_path)
    filename_no_ext = os.path.splitext(filename)[0]

    # Upload the archive to /tmp/ directory on the web server
    put(archive_path, "/tmp/{}".format(filename))

    # Create the release directory
    run("mkdir -p /data/web_static/releases/{}/".format(filename_no_ext))

    # Uncompress the archive to the release directory
    run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/".format(filename, filename_no_ext))

    # Remove the uploaded archive
    run("rm /tmp/{}".format(filename))

    # Move the contents to the proper location
    run("mv /data/web_static/releases/{}/web_static/* /data/web_static/releases/{}/".format(filename_no_ext, filename_no_ext))

    # Remove the empty web_static directory
    run("rm -rf /data/web_static/releases/{}/web_static".format(filename_no_ext))

    # Remove the current symbolic link
    run("rm -rf /data/web_static/current")

    # Create a new symbolic link to the new version
    run("ln -s /data/web_static/releases/{}/ /data/web_static/current".format(filename_no_ext))

    print("New version deployed!")

    return True

def deploy():
    """
    Calls the do_pack() function and stores the path of the created archive.
    Calls the do_deploy(archive_path) function using the new path of the new archive.

    Returns:
        True if all operations are done correctly, False otherwise.
    """
    # Call do_pack() and store the path of the created archive
    archive_path = do_pack()

    # Return False if no archive has been created
    if archive_path is None:
        return False

    # Call do_deploy(archive_path) function
    return do_deploy(archive_path)

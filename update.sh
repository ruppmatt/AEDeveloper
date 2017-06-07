#!/bin/sh

sudo git pull && sudo chown -R www-data * && sudo service apache2 restart


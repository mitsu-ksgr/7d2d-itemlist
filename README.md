7d2d-itemlist
=============

7daystodie simple item list generator.


You must put 7daystodie/application/Data to 7d2d_app direcotry before execute.

1. cd THIS_PROJECT_ROOT
2. cp -R /opt/7daystodie/application/Data ./7d2d_app
3. ./run.sh -f json -o out/out.json ./7d2d_app/Data
4. ls out/  #> out/out.json


### Notes
- in alpha19.1, items.xml has data of Impact Driver, but doesn't have a icon
  of it in `ItemIcons` directory.
  - you need to get `meleeToolSalvageT3ImpactDriver.png` from somewhere,
    then put it to `ItemIcons` directory.

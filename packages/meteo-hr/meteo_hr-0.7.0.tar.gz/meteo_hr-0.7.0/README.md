meteo.hr CLI
============

Commandline tool for displaying the [three-day forecast from meteo.hr](http://meteo.hr/prognoze.php?section=prognoze_model&param=3d).

Install:

```
pip install --user meteo_hr
```

Usage:

```
meteo <place>
```

For example:

```
meteo zagreb
```

![Forecast for Zagreb](forecast.png)

List available places:

```
meteo --list
```

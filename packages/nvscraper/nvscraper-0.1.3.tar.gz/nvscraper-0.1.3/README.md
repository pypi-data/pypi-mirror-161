
<h1 align="center">The Unofficial Nvidia Web Scraper</h1>

<div align="center">
    <img src="./nvscraper.gif">
</div>


<h4 align="center">A simple Nvidia Store API integration with Python.

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#requirements">Requirements</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#to-do">To Do</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>

## Key Features
* Available [Graphics Cards, Manufacturers and Attributes](./docs/consts.md) 
* Select specific graphic_cards, manufacturers, location or min and max prices:
    ```python
    nv_scraper = NvidiaScraper(
        # Select Graphics Cards to Scrape (Available in GRAPHICS_CARD)
        graphics_card = ['RTX 3070',
        'RTX 2080 TI',
        'RTX 3090',
        ...
        ],
        # Select Graphics Cards to Scrape (Available in MANUFACTURERS)
        manufacturers = ['Nvidia',
        'Aorus',
        'Acer',
        ...
        ],
        # Select location (Example of Spain: es-es)
        locale = 'es-es',
        # Select price range -> (min, max)
        price_range = (400, 1500)
    )
    ```
* Filter the data 
  - List of available attributes can be found on the <i><b>ATTRIBUTES</b></i> variable inside the library.
  - An example could be <em>(Filters only not available products)</em>:
  ```python
    nv_scraper = NvidiaScraper() # Inicialize the NvidiaScraper
    nv_scraper.refresh_data()   # Refresh data
    nv.scrapper.get_data().filter_by(
        productAvailable = False # Only get not available products
    )

    >>> 'NVIDIA GEFORCE RTX 3070': {
            'productID': 30056, 
            'productAvailable': False, <-
            'productTitle': 'NVIDIA GEFORCE RTX 3070', 
            ...
        }, 
        ...
    ```
* Get Data JSon formatted
     ```python
    nv_scraper = NvidiaScraper() # Inicialize the NvidiaScraper
    nv_scraper.refresh_data()   # Refresh data
    nv_scraper.get_data() # Returns in Json Format

    >>> 'NVIDIA GEFORCE RTX 3070': {
            'productID': 30056, 
            'productAvailable': False, <-
            'productTitle': 'NVIDIA GEFORCE RTX 3070', 
            ...
        }, 
        ...
    ```
* Cross platform
  - Windows, macOS and Linux ready.

## Requirements

In order to use this library, you will need these packages:

* Requests

## How To Use

```bash
# Install the library
$ pip install nvscraper
```

You can go [here]() for the latest installable version of nv-scraper for Windows, macOS and Linux.

To get the data, it is necessary to <em>refresh_data()</em> when a change in the options occurs, such as the graphic cards chosen, manufacturers, the locality, etc...

```python
    nv_scraper = NvidiaScraper()
    nv_scraper.get_data()

    >>> {}

    nv_scraper.refresh_data()
    nv_scraper.get_data()

    >>> 'NVIDIA GEFORCE RTX 3070': {
            'productID': 30056, 
            'productAvailable': False, <-
            'productTitle': 'NVIDIA GEFORCE RTX 3070', 
            ...
        }, 
        ...
```

## To Do 

To Do list for next updates:
* Improve Docummentation
* Get Information about retrailers
* Make a bash version
* ...

## Credits

This software uses the following things:

- [Requests Library](https://github.com/psf/requests)
- [Nvidia API](nvidia.com)

## License

MIT

---

> GitHub [@covicale](https://github.com/covicale) &nbsp;&middot;&nbsp;
> Twitter [@covicale](https://twitter.com/covicale)
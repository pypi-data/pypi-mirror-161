# OSU Course Analytics (Osuca)

Analyze student review responses for courses in the Computer Science (CS) program of Oregon State University (OSU)

## Description

This program allows analyzing [the online survey of course reviews](https://docs.google.com/forms/d/e/1FAIpQLSeAWZa_OWYqwOte5yw4loGgE6hEUqOJOeSpmzStZF_HcufufQ/viewform) from the CS students in OSU. It helps students answer questions such as:

- Does course difficulty vary from term to term?
- Does course difficulty increase if I take other courses in the same quarter?
- Which course combinations are most difficult taken together?

It also exposes several services for client programs to query course analytics in JSON format. See [Communication Contract](#communication-contract) for further details. 

## Getting Started

### Dependencies

Osuca requires Python 3.7 and newer. It can run on any operating system with Python.

### Installing

#### Create a virtual environment and activate it.

##### macOS/Linux

```
$ mkdir osuca
$ cd osuca
$ python3 -m venv venv
$ . venv/bin/activate
```

##### Windows

```
> mkdir myproject
> cd myproject
> py -3 -m venv venv
> venv\Scripts\activate
```

#### Install Osuca and dependencies from PyPI

```
(venv) pip install osuca
```

### Executing program

#### Set environment variables

##### macOS/Linux

```
$ export FLASK_APP=osuca
$ export OSUCA_DATA_SOURCE='https://docs.google.com/spreadsheets/d/1MFBGJbOXVjtThgj5b6K0rv9xdsC1M2GQ0pJVB-8YCeU/export?format=csv'
```

##### Windows

```
> $env:FLASK_APP = "osuca"
> $env:OSUCA_DATA_SOURCE = "https://docs.google.com/spreadsheets/d/1MFBGJbOXVjtThgj5b6K0rv9xdsC1M2GQ0pJVB-8YCeU/export?format=csv"
```

#### Run Osuca

```
flask run
```

View output in your browser at `http://localhost:5000`

## Communication Contract

Osuca returns **JSON** objects for the following valid **HTTP GET** requests:

- /courses
- /course-year-aggregates
- /course-quarter-aggregates

For example, `$curl http://localhost:5000/courses` will return a JSON list of course objects to the clients.

### UML Sequence Diagram

As shown in the diagram, Osuca requests a CSV document that resides in Google documents containing the scraped student responses. Then it serves the contents of this document in JSON form to clients.

![alt text][osuca sequence uml]

[osuca sequence uml]: https://github.com/ozbakan/osuca/blob/master/docs/images/uml-sequence.png "Osuca Sequence UML"

### Service Details

The following shows example responses to the requests.

/courses

```
[
  {
    "subject": "CS",
    "id": "419",
    "name": "Capstone"
  },
  {
    "subject": "CS",
    "id": "325",
    "name": "Analysis of Algorithms"
  }, …
]
```

/course-year-aggregates

```
 [
  {
    "course": {
      "subject": "CS",
      "id": "261",
      "name": "Data Structures"
    },
    "year": "2018",
    "aggregate": {
      "count": 11,
      "sum": 31,
      "mean": 2.81
    }
  }, …
 ]
```

/course-quarter-aggregates

```
[
  {
    "course": {
      "subject": "CS",
      "id": "290",
      "name": "Web Development"
    },
    "quarter": {
      "term": "Spring",
      "year": "2022"
    },
    "aggregate": {
      "count": 6,
      "sum": 15,
      "mean": 2.5
    }
  }, …
]
```

## Authors

Tolga Ozbakan | tolga@ozbakan.com


## License

This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

Inspiration, code snippets, etc.

- [A simple README.md template](https://gist.github.com/DomPizzie/7a5ff55ffa9081f2de27c315f5018afc)

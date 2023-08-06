A python package containing dictionary representations of Avro Schemas,
for use with the nubium project.

## Usage Examples
The first step is to include the latest version of the schema library in
the requirements for the app.
For code examples, go to https://gitlab.corp.redhat.com/ebrennan/python-avro-classes.git

When a git tag is created, the `.gitlab-ci.yml` pipeline will automatically 
trigger `upload_package.sh`, creating a new pypi version.

### Faust
1) Import one of the schema dictionaries from the package
1) Dump the dictionary to a string using `json.dumps`
1) Define a serializer using the `FaustSerializer` class

### Confluent Kafka
1) Import the schema dictionary
1) Dump the schema to a string using `json.dumps`
1) Create a schema object using `confluent_kafka.avro.loads`
1) Use the schema when instantiating Avro producer and consumer clients

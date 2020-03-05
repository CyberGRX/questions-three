# Amazon Web Services Integrations for Questions Three

This is an optional package for the [Questions Three testing library](https://pypi.org/project/questions-three/).

## S3 Artifact Saver

As the name implies, the S3 Artifact Saver saves artifacts to an AWS S3 bucket.  It subscribes to `ARTIFACT_CREATED` and `REPORT_CREATED` events and saves everything it sees. Among other things, this will include JUnit XML test reports, HTTP transcripts from the built-in HTTP Client, and screenshots and DOM dumps from the [optional Selenium integrations](https://pypi.org/project/questions-three-selenium).

### Activation

Create (or append) a custom reporters file:

```
echo questions_three_aws.s3_artifact_saver.S3ArtifactSaver >> /var/custom_reporters
```

Inform Questions Three about the custom reporters file:

```
export CUSTOM_REPORTERS_FILE=/var/custom_reporters
```

Tell the S3 Artifact Saver which bucket to use:

```
export S3_BUCKET_FOR_ARTIFACTS=spam-eggs-sausage-spam
```

(Optional) Specify an object(folder) prefix to which test runs will be saved within the specified bucket:

```
export S3_PREFIX_OBJECT_NAME=some_test_runner
```

Set appropriate environment variables for AWS:

See [the fine AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html).  At a minimum, you will need credentials and a region.

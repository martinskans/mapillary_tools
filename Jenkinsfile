#!groovy
@Library('mapillary-pipeline') _
com.mapillary.pipeline.Pipeline.builder(this, steps)
    .withBuildStage()
    .withIntegrationStage()
    .withReleaseOsxStage()
    .withReleaseWindowsStage()
    .withSignIosStage()
    .withPublishStage()
    .build()
    .execute()

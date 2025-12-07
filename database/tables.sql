CREATE TABLE `courtbookings` (
  `CBId` BIGINT,
  `CourtBookingSource` VARCHAR(255),
  `CourtBookingPropertyCode` VARCHAR(255),
  `VersionStamp` VARBINARY(255),
  `CreatedWhen` TIMESTAMP,
  `LastModifiedWhen` TIMESTAMP,
  `CourtBookingConfId` VARCHAR(255),
  `BookingTypeID` VARCHAR(255),
  `BookingTypeDescription` VARCHAR(255),
  `BookingStatus` VARCHAR(255),
  `StartWhen` TIMESTAMP,
  `EndWhen` TIMESTAMP,
  `CourtTypeID` VARCHAR(255),
  `CourtTypeDescription` VARCHAR(255),
  `NumberOfPlayers` BIGINT,
  `BookingSalesValue` TEXT,
  `PlayerSalesValue` TEXT,
  `IsTBDPlayer` BOOLEAN,
  `IsNoShow` BOOLEAN,
  `IsCheckedIn` BOOLEAN,
  `OnSite` BOOLEAN,
  `Location` VARCHAR(255),
  `CourtName` VARCHAR(255),
  `InstructorID` VARCHAR(255),
  `InstructorName` VARCHAR(255),
  `CancellationNumber` VARCHAR(255),
  `CancellationFee` TEXT,
  `ProfileId` BIGINT
);

CREATE TABLE `lessonbookings` (
  `LBId` BIGINT,
  `LessonBookingSource` VARCHAR(255),
  `LessonBookingPropertyCode` VARCHAR(255),
  `VersionStamp` VARBINARY(255),
  `CreatedWhen` TIMESTAMP,
  `LastModifiedWhen` TIMESTAMP,
  `LessonBookingConfId` VARCHAR(255),
  `StartWhen` TIMESTAMP,
  `EndWhen` TIMESTAMP,
  `LessonType` VARCHAR(255),
  `InstructorName` VARCHAR(255),
  `LessonDescription` VARCHAR(255),
  `FacilityName` VARCHAR(255),
  `OnSite` INT,
  `Location` VARCHAR(255),
  `FacilityInfo` INT,
  `EquipmentProvided` VARCHAR(255),
  `BookingStatus` VARCHAR(255),
  `IsPaid` BOOLEAN,
  `LessonSalesValue` TEXT,
  `ReservationID` VARCHAR(255),
  `ReservationStatus` VARCHAR(255),
  `ReservationSource` INT,
  `CancellationNumber` VARCHAR(255),
  `CancellationFee` TEXT,
  `IsTBDPlayer` BOOLEAN,
  `IsNoShow` BOOLEAN,
  `IsCheckedIn` BOOLEAN,
  `ProfileId` BIGINT,
  `TotalSpent` TEXT
);

CREATE TABLE `otherreservations` (
  `ORId` BIGINT,
  `ProfileId` BIGINT,
  `ReservationSource` VARCHAR(255),
  `ReservationSourcePropertyCode` VARCHAR(255),
  `VersionStamp` VARBINARY(255),
  `CreatedWhen` TIMESTAMP,
  `LastModifiedWhen` TIMESTAMP,
  `ReservationId` VARCHAR(255),
  `ReservationConfId` VARCHAR(255),
  `ActivityName` VARCHAR(255),
  `ActivityDescription` VARCHAR(255),
  `PartySize` BIGINT,
  `StartWhen` TIMESTAMP,
  `FacilityName` VARCHAR(255),
  `OnSite` BOOLEAN,
  `Location` VARCHAR(255),
  `TotalSpent` TEXT
);

CREATE TABLE `pmspreferences` (
  `PMSPrefId` INT,
  `ProfileId` INT,
  `PMSSource` INT,
  `PMSSourcePropertyCode` INT,
  `PMSSId` INT,
  `CreatedWhen` INT,
  `LastModifiedWhen` INT,
  `PreferenceName` INT,
  `PreferenceDescription` INT,
  `PreferenceValue` INT,
  `Details` INT
);

CREATE TABLE `pmsstayprofileassociations` (
  `PSPAId` BIGINT,
  `PMSConfId` VARCHAR(255),
  `MasterProfileId` BIGINT,
  `AssociatedProfileId` BIGINT,
  `CreatedWhen` TIMESTAMP
);

CREATE TABLE `pmsstays` (
  `PMSSId` BIGINT,
  `ProfileId` BIGINT,
  `PMSSource` VARCHAR(255),
  `PMSSourcePropertyCode` VARCHAR(255),
  `VersionStamp` VARBINARY(255),
  `CreatedWhen` TIMESTAMP,
  `LastModifiedWhen` TIMESTAMP,
  `PMSStayID` VARCHAR(255),
  `PMSConfID` VARCHAR(255),
  `PMSCRSID` VARCHAR(255),
  `PMSFolioID` VARCHAR(255),
  `FirstName` INT,
  `LastName` INT,
  `ArrivalWhen` TIMESTAMP,
  `DepartureWhen` TIMESTAMP,
  `StayStatus` VARCHAR(255),
  `RoomNumber` VARCHAR(255),
  `RoomType` VARCHAR(255),
  `RoomTypeDescription` VARCHAR(255),
  `RoomDetail` VARCHAR(255),
  `Adults` BIGINT,
  `ArrivalRateCode` VARCHAR(255),
  `TotalRevenue` TEXT,
  `CancellationNumber` VARCHAR(255),
  `ChildOver` BIGINT,
  `ChildUnder` BIGINT,
  `GroupCode` VARCHAR(255),
  `IsCancelled` BOOLEAN
);

CREATE TABLE `poolbeachamenityreservations` (
  `PBARId` BIGINT,
  `ProfileId` BIGINT,
  `PBASource` VARCHAR(255),
  `PBASourcePropertyCode` VARCHAR(255),
  `VersionStamp` VARBINARY(255),
  `CreatedWhen` TIMESTAMP,
  `LastModifiedWhen` TIMESTAMP,
  `PBAType` VARCHAR(255),
  `PoolBeachName` VARCHAR(255),
  `PBANumber` VARCHAR(255),
  `MaxGuests` BIGINT,
  `StartWhen` TIMESTAMP,
  `CompletesWhen` TIMESTAMP,
  `CancellationNumber` INT,
  `ConfId` VARCHAR(255),
  `Location` VARCHAR(255),
  `PriceQuoted` TEXT
);

CREATE TABLE `preferences` (
  `PrefId` BIGINT,
  `ProfileId` BIGINT,
  `CreatedWhen` TIMESTAMP,
  `LastModifiedWhen` TIMESTAMP,
  `PreferenceName` VARCHAR(255),
  `PreferenceDescription` VARCHAR(255),
  `PreferenceValue` VARCHAR(255),
  `Details` VARCHAR(255),
  `PreferenceSource` VARCHAR(255),
  `PreferenceSourcePropertyCode` VARCHAR(255),
  `MergedFrom` INT
);

CREATE TABLE `profileassociationrelationships` (
  `PARId` BIGINT,
  `RelationA` VARCHAR(255),
  `RelationB` VARCHAR(255)
);

CREATE TABLE `profileassociations` (
  `PAId` BIGINT,
  `Profile1Id` BIGINT,
  `Profile2Id` BIGINT,
  `Relation` VARCHAR(255),
  `Details` INT,
  `CreatedWhen` TIMESTAMP,
  `LastModifiedWhen` TIMESTAMP,
  `AssocSource` VARCHAR(255),
  `AssocSourcePropertyCode` VARCHAR(255)
);

CREATE TABLE `profilemonthlyspend` (
  `PMSId` BIGINT,
  `ProfileId` BIGINT,
  `Month` BIGINT,
  `Year` BIGINT,
  `Revenue` TEXT,
  `RevenueType` VARCHAR(255)
);

CREATE TABLE `profiles` (
  `PId` BIGINT,
  `PublicGUID` VARCHAR(255),
  `PublicHashId` TEXT,
  `VersionStamp` VARBINARY(255),
  `CreatedWhen` TIMESTAMP,
  `LastModifiedWhen` TIMESTAMP,
  `IsActive` BOOLEAN,
  `RetentionRevoked` BOOLEAN,
  `MergedTo` INT,
  `ProfileSource` VARCHAR(255),
  `ProfileSourcePropertyCode` VARCHAR(255),
  `Pronouns` VARCHAR(255),
  `Salutation` VARCHAR(255),
  `FirstName` VARCHAR(255),
  `LastName` VARCHAR(255),
  `MiddleName` VARCHAR(255),
  `Nickname` VARCHAR(255),
  `Suffix` VARCHAR(255),
  `BirthDate` TIMESTAMP,
  `Sosh` VARCHAR(255),
  `Gender` VARCHAR(255),
  `PrimaryEmail` VARCHAR(255),
  `PrimaryPhone` VARCHAR(255),
  `BusinessTitle` VARCHAR(255),
  `Profession` VARCHAR(255),
  `PrimaryCategory` INT,
  `Comments` VARCHAR(255),
  `PrimaryAddressType` VARCHAR(255),
  `PrimaryAddress1` VARCHAR(255),
  `PrimaryAddress2` VARCHAR(255),
  `PrimaryCity` VARCHAR(255),
  `PrimaryState` VARCHAR(255),
  `PrimaryPostalCode` VARCHAR(255),
  `PrimaryCountry` VARCHAR(255),
  `VIPStatus` VARCHAR(255),
  `GoldenRecord` INT,
  `ProfileType` VARCHAR(255),
  `IsAnonymized` BOOLEAN,
  `AnonymizedBy` INT,
  `AnonymizedDate` INT,
  `AnniversaryDate` INT,
  `VIPStatusDescription` VARCHAR(255),
  `PrimaryPhoneType` VARCHAR(255),
  `PrimaryStateCode` VARCHAR(255),
  `PrimaryCountryCode` VARCHAR(255),
  `IsVIP` BOOLEAN,
  `PrimaryLoyaltyID` VARCHAR(255),
  `PrimaryLoyaltyLevel` VARCHAR(255),
  `PrimaryLoyaltyProgram` VARCHAR(255),
  `PrimaryPhoneTechType` VARCHAR(255),
  `PrimaryPhoneCountryCode` VARCHAR(255),
  `IsPlaceholder` BOOLEAN,
  `AverageVisitsPerYear` TEXT,
  `AverageSpendPerVisit` TEXT,
  `AverageDailySpend` INT,
  `AverageActivitiesPerYear` INT,
  `TotalSpent` TEXT
);

CREATE TABLE `profilevisitsperyear` (
  `PVPYId` BIGINT,
  `ProfileId` BIGINT,
  `VisitCount` TEXT
);

CREATE TABLE `removedprofilemergecandidates` (
  `RPMCId` INT,
  `ProfileId` INT,
  `RemovedMergeCandidatePId` INT,
  `RemovedWhen` INT
);

CREATE TABLE `restaurantreservations` (
  `RRId` BIGINT,
  `ProfileId` BIGINT,
  `RestaurantSource` VARCHAR(255),
  `RestaurantSourcePropertyCode` VARCHAR(255),
  `VersionStamp` VARBINARY(255),
  `CreatedWhen` TIMESTAMP,
  `LastModifiedWhen` TIMESTAMP,
  `RestaurantReservationId` VARCHAR(255),
  `RestaurantConfId` VARCHAR(255),
  `ReservationStatus` VARCHAR(255),
  `OnSite` BOOLEAN,
  `PartySize` BIGINT,
  `StartWhen` TIMESTAMP,
  `SpecialOccasion` VARCHAR(255),
  `CustomerDietaryRestrictions` VARCHAR(255),
  `GuestDietaryRestrictions` VARCHAR(255),
  `RestaurantName` VARCHAR(255),
  `RestaurantDetails` VARCHAR(255),
  `CancellationNumber` VARCHAR(255),
  `TotalSpent` TEXT,
  `IsCancelled` BOOLEAN
);

CREATE TABLE `settings` (
  `SettingId` BIGINT,
  `SettingName` VARCHAR(255),
  `StringValue` INT,
  `BitValue` BOOLEAN,
  `DateTimeValue` TIMESTAMP,
  `IntValue` TEXT,
  `BigIntValue` INT,
  `MoneyValue` INT,
  `NumericValue` INT
);

CREATE TABLE `spabookings` (
  `SBId` BIGINT,
  `ProfileId` BIGINT,
  `SpaSource` VARCHAR(255),
  `SpaSourcePropertyCode` VARCHAR(255),
  `VersionStamp` VARBINARY(255),
  `CreatedWhen` TIMESTAMP,
  `LastModifiedWhen` TIMESTAMP,
  `SpaBookingId` VARCHAR(255),
  `SpaConfID` VARCHAR(255),
  `StartWhen` TIMESTAMP,
  `EndWhen` TIMESTAMP,
  `BookingStatus` VARCHAR(255),
  `ActivityType` VARCHAR(255),
  `ActivityName` VARCHAR(255),
  `ActivityDescription` VARCHAR(255),
  `ProviderName` VARCHAR(255),
  `ProviderGender` VARCHAR(255),
  `FacilityName` VARCHAR(255),
  `Price` TEXT,
  `CancellationNumber` VARCHAR(255),
  `CancellationFee` TEXT,
  `SpaName` VARCHAR(255),
  `SpaAddress1` VARCHAR(255),
  `SpaAddress2` VARCHAR(255),
  `SpaCity` VARCHAR(255),
  `SpaState` VARCHAR(255),
  `SpaPostalCode` VARCHAR(255),
  `HealthNotes` VARCHAR(255),
  `ReservationNotes` VARCHAR(255),
  `AppointmentNotes` VARCHAR(255),
  `GuestNotes` VARCHAR(255),
  `CancellationPolicy` VARCHAR(255),
  `ProviderGenderPreference` VARCHAR(255),
  `FacilityGenderPreference` VARCHAR(255),
  `MainGuestType` VARCHAR(255),
  `WellnessFormCompleted` BOOLEAN,
  `WellnessFormExpired` BOOLEAN,
  `WellnessFormSent` BOOLEAN,
  `FirstTimeGuest` BOOLEAN,
  `IsCancelled` BOOLEAN
);

CREATE TABLE `spapreferences` (
  `SpaPrefId` INT,
  `ProfileId` INT,
  `SpaSource` INT,
  `SpaSourcePropertyCode` INT,
  `SBId` INT,
  `CreatedWhen` INT,
  `LastModifiedWhen` INT,
  `PreferenceName` INT,
  `PreferenceDescription` INT,
  `PreferenceValue` INT,
  `Details` INT
);

CREATE TABLE `sysdiagrams` (
  `name` VARCHAR(255),
  `principal_id` BIGINT,
  `diagram_id` BIGINT,
  `version` BIGINT,
  `definition` VARBINARY(255)
);

CREATE TABLE `teetimebookings` (
  `TTBId` BIGINT,
  `ProfileId` BIGINT,
  `TeeTimeSource` VARCHAR(255),
  `TeeTimeSourcePropertyCode` VARCHAR(255),
  `VersionStamp` VARBINARY(255),
  `CreatedWhen` TIMESTAMP,
  `LastModifiedWhen` TIMESTAMP,
  `BookingType` VARCHAR(255),
  `IsGroupBooking` BOOLEAN,
  `GroupBookingID` VARCHAR(255),
  `TeeTimeConfId` VARCHAR(255),
  `BookingStatus` VARCHAR(255),
  `CourseName` VARCHAR(255),
  `BookedDate` TIMESTAMP,
  `StartingHole` BIGINT,
  `CancellationPolicyText` VARCHAR(255),
  `CancellationDeadlineDateTime` TIMESTAMP,
  `BookingNotes` VARCHAR(255),
  `Disclaimer` VARCHAR(255),
  `CourseInformation` VARCHAR(255),
  `NumberOfPlayers` BIGINT,
  `BookingSalesValue` TEXT,
  `PlayerSalesValue` TEXT,
  `IsTBDPlayer` BOOLEAN,
  `NumberOfHoles` BIGINT,
  `Transportation` VARCHAR(255),
  `Caddy` VARCHAR(255),
  `DidNotPlay` BOOLEAN,
  `IsCheckedIn` BOOLEAN,
  `IsCancelled` INT
);

CREATE TABLE `transportationreservations` (
  `ReservationSource` VARCHAR(255),
  `ReservationSourcePropertyCode` VARCHAR(255),
  `VersionStamp` VARBINARY(255),
  `CreatedWhen` TIMESTAMP,
  `LastModifiedWhen` TIMESTAMP,
  `ReservationType` VARCHAR(255),
  `Driver` VARCHAR(255),
  `Destination` VARCHAR(255),
  `NumberOfGuests` BIGINT,
  `PickupLocation` VARCHAR(255),
  `StartWhen` TIMESTAMP,
  `ProfileId` BIGINT,
  `TotalSpent` TEXT
);

CREATE TABLE `vipcodes` (
  `VCId` BIGINT,
  `Code` VARCHAR(255)
);

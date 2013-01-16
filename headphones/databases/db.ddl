CREATE TABLE albums
(
    ArtistID text,
    ArtistName text,
    AlbumTitle text,
    AlbumASIN text,
    ReleaseDate text,
    DateAdded text,
    AlbumID text,
    Status text,
    Type text,
    ArtworkURL text,
    ThumbURL text,
    ReleaseID text,
    ReleaseFormat text,
    ReleaseCountry text,
    SearchTerm text
);
CREATE TABLE allalbums
(
    ArtistID text,
    ArtistName text,
    AlbumTitle text,
    AlbumASIN text,
    ReleaseDate text,
    AlbumID text,
    Type text,
    ReleaseID text,
    ReleaseCountry text,
    ReleaseFormat text
);
CREATE TABLE alltracks
(
    ArtistID text,
    ArtistName text,
    AlbumTitle text,
    AlbumASIN text,
    AlbumID text,
    TrackTitle text,
    TrackDuration text,
    TrackID text,
    TrackNumber integer,
    Location text,
    BitRate integer,
    CleanName text,
    Format text,
    ReleaseID text
);
CREATE TABLE artists
(
    ArtistID text,
    ArtistName text,
    ArtistSortName text,
    DateAdded text,
    Status text,
    IncludeExtras integer,
    LatestAlbum text,
    ReleaseDate text,
    AlbumID text,
    HaveTracks integer,
    TotalTracks integer,
    LastUpdated text,
    ArtworkURL text,
    ThumbURL text,
    Extras text
);
CREATE TABLE blacklist
(
    ArtistID text
);
CREATE TABLE descriptions
(
    ReleaseGroupID text,
    ReleaseID text,
    Summary text,
    Content text,
    ArtistID text,
    LastUpdated text
);
CREATE TABLE have
(
    ArtistName text,
    AlbumTitle text,
    TrackNumber text,
    TrackTitle text,
    TrackLength text,
    BitRate text,
    Genre text,
    Date text,
    TrackID text,
    Location text,
    CleanName text,
    Format text,
    Matched text
);
CREATE TABLE lastfmcloud
(
    ArtistName text,
    ArtistID text,
    Count integer
);
CREATE TABLE newartists
(
    ArtistName text
);
CREATE TABLE releases
(
    ReleaseID text,
    ReleaseGroupID text
);
CREATE TABLE snatched
(
    AlbumID text,
    Title text,
    Size integer,
    URL text,
    DateAdded text,
    Status text,
    FolderName text,
    Kind text
);
CREATE TABLE tracks
(
    ArtistID text,
    ArtistName text,
    AlbumTitle text,
    AlbumASIN text,
    AlbumID text,
    TrackTitle text,
    TrackDuration text,
    TrackID text,
    TrackNumber integer,
    Location text,
    BitRate integer,
    CleanName text,
    Format text,
    ReleaseID text
);
CREATE UNIQUE INDEX album_artistid_reldate ON albums ( ArtistID, ReleaseDate );
CREATE UNIQUE INDEX alltracks_trackid_albumtitle ON alltracks ( TrackID, AlbumTitle );
CREATE UNIQUE INDEX alltracks_trackid_releaseid ON alltracks ( TrackID, ReleaseID );
CREATE UNIQUE INDEX tracks_trackid_albumid ON tracks ( TrackID, AlbumID );
CREATE UNIQUE INDEX tracks_artistid ON tracks ( ArtistID );
CREATE UNIQUE INDEX tracks_albumid ON tracks ( AlbumID );

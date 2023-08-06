#pragma once

#include "inc_libCzi.h"
#include "PImage.h"
#include <iostream>
#include <optional>

/// Class used to represent a CZI writer object in pylibCZIrw. 
/// It gathers the libCZI features for writing needed in the pylibCZI project.
/// CZIrwAPI will be exposed to python via pybind11 as a czi class.
class CZIwriteAPI
{

private:
	std::shared_ptr <libCZI::ICziWriter>	spWriter_;	///< The pointer to the spWriter.
	libCZI::Utils::CompressionOption defaultCompressionOptions_;
public:

    /// Constructor which constructs a CZIwriteAPI object from the given wstring. Creates a
    /// spWriter for the czi document pointed by the given filepath. This constructor will use
    /// default options for compression, which is "no compression, uncompressed".
    ///
    /// \param  fileName    Filename of the CZI-file to be created.
	CZIwriteAPI(const std::wstring& fileName);

    /// Constructor creating a CZI-writer object for the specified filename. The 'compressionOptions'
    /// argument gives a string representation of the compression options to be used as default for
    /// this instance.
    ///
    /// \param  fileName            Filename of the file.
    /// \param  compressionOptions  The compression-options in string representation.
	CZIwriteAPI(const std::wstring& fileName, const std::string& compressionOptions);

	/// Close the Opened czi writer.
	void close() { this->spWriter_->Close(); }

	void WriteMetadata(const std::wstring& documentTitle, std::optional<double> scaleX, std::optional<double> scaleY, std::optional<double> scaleZ, const std::map<int, std::string>& channelNames, const std::map<std::string, const libCZI::CustomValueVariant>& customAttributes);

    /// Add the specified bitmap plane to the czi document at the specified coordinates.
    ///
    /// \param  coordinateString    The coordinate in string representation.
    /// \param  plane               The bitmap to add.
    /// \param  x                   The x pixel coordinate.
    /// \param  y                   The y pixel coordinate.
    /// \param  m                   The m index.
    ///
    /// \returns    True if it succeeds, false if it fails.
	bool AddTile(const std::string& coordinateString, const PImage* plane, int x, int y, int m, const std::string& retiling_id);

    /// Add the specified bitmap plane to the czi document at the specified coordinates. This method allows to override the
    /// compression-options. If the string 'compressionOptions' is empty, then the default compression-options are used.
    ///
    /// \param  coordinateString    The coordinate in string representation.
    /// \param  plane               The bitmap to add.
    /// \param  x                   The x pixel coordinate.
    /// \param  y                   The y pixel coordinate.
    /// \param  m                   The m index.
    /// \param  compressionOptions  The compression-options in string representation.
    ///
    /// \returns    True if it succeeds, false if it fails.
	bool AddTileEx(const std::string& coordinateString, const PImage* plane, int x, int y, int m, const std::string& compressionOptions, const std::string& retiling_id);
private:
    static std::string CreateSubBlockMetadataXml(const std::string& retiling_id);

	static void AddSubBlock(const libCZI::CDimCoordinate& coord, const PImage* subblock, const libCZI::Utils::CompressionOption& compressionOptions, libCZI::ICziWriter* writer, int x, int y, int m, const std::string& sbmetadata);
};
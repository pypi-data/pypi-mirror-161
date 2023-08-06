#include "CZIreadAPI.h"

using namespace libCZI;
using namespace std;


CZIreadAPI::CZIreadAPI(const std::wstring& fileName) {

	auto stream = libCZI::CreateStreamFromFile(fileName.c_str());
	auto spReader = libCZI::CreateCZIReader();
	spReader->Open(stream);
	
	this->spAccessor = spReader->CreateSingleChannelScalingTileAccessor();
	this->spReader = spReader;
}


std::string CZIreadAPI::GetXmlMetadata() {

	auto mds = this->spReader->ReadMetadataSegment();
	auto md = mds->CreateMetaFromMetadataSegment();

	return md->GetXml();
}

size_t CZIreadAPI::GetDimensionSize(libCZI::DimensionIndex DimIndex) {

	auto stats = this->spReader->GetStatistics();
	int size;

	// Should replace nullptr with reference to handle CZI with index not starting at 0, legal ?
	bool DimExist = stats.dimBounds.TryGetInterval(DimIndex, nullptr, &size);

	if (DimExist) {
		return size;
	}
	
	return 0;
}

libCZI::PixelType CZIreadAPI::GetChannelPixelType(int chanelIdx) {

	libCZI::SubBlockInfo sbBlkInfo;

	bool b = this->spReader->TryGetSubBlockInfoOfArbitrarySubBlockInChannel(chanelIdx, sbBlkInfo);
	if (!b) {
		// TODO more precise error handling
		return libCZI::PixelType::Invalid;
	}

	return sbBlkInfo.pixelType;
}


libCZI::SubBlockStatistics CZIreadAPI::GetSubBlockStats() {
	
	return this->spReader->GetStatistics();
}

std::unique_ptr<PImage> CZIreadAPI::GetSingleChannelScalingTileAccessorData(libCZI::PixelType pixeltype, libCZI::IntRect roi, libCZI::RgbFloatColor bgColor, float zoom, const std::string& coordinateString, const std::wstring& SceneIndexes) {


	libCZI::CDimCoordinate planeCoordinate;
	try
	{
		planeCoordinate = CDimCoordinate::Parse(coordinateString.c_str());
	}
	catch (libCZI::LibCZIStringParseException& parseExcp)
	{
		//TODO Error handling
	}

	libCZI::ISingleChannelScalingTileAccessor::Options scstaOptions; scstaOptions.Clear();
	scstaOptions.backGroundColor = bgColor;
	if (!SceneIndexes.empty()) {
		scstaOptions.sceneFilter = libCZI::Utils::IndexSetFromString(SceneIndexes);
	}
	
	std::shared_ptr<libCZI::IBitmapData> Data = this->spAccessor->Get(pixeltype, roi, &planeCoordinate, zoom, &scstaOptions);
	std::unique_ptr<PImage> ptr_Bitmap(new PImage(Data));

	return ptr_Bitmap;
}

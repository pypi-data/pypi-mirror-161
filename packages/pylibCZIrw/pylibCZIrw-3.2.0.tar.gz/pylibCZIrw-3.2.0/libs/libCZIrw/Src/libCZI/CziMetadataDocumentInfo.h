//******************************************************************************
// 
// libCZIrw is a reader and writer for the CZI fileformat written in C++
// Copyright (C) 2017  Zeiss Microscopy GmbH
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
// 
// To obtain a commercial version please contact Zeiss Microscopy GmbH.
// 
//******************************************************************************

#pragma once

#include <map>

#include "libCZI.h"
#include "CziMetadata.h"

class CCziMetadataDocumentInfo : public libCZI::ICziMultiDimensionDocumentInfo
{
private:
	std::shared_ptr<CCziMetadata>	metadata;
	std::map < libCZI::DimensionIndex, std::shared_ptr<libCZI::IDimensionInfo>> dimensions;
public:
	CCziMetadataDocumentInfo(std::shared_ptr<CCziMetadata> md);

public:	// interface ICziMultiDimensionDocumentInfo
	virtual libCZI::GeneralDocumentInfo GetGeneralDocumentInfo() const override;
	virtual libCZI::ScalingInfoEx GetScalingInfoEx() const override;
	virtual libCZI::ScalingInfo GetScalingInfo() const override;
	virtual void EnumDimensions(const std::function<bool(libCZI::DimensionIndex)>& enumDimensions) override;
	virtual std::shared_ptr<libCZI::IDimensionInfo> GetDimensionInfo(libCZI::DimensionIndex dim) override;
	virtual std::shared_ptr<libCZI::IDimensionZInfo> GetDimensionZInfo() override;
	virtual std::shared_ptr<libCZI::IDimensionTInfo> GetDimensionTInfo() override;
	virtual std::shared_ptr<libCZI::IDimensionsChannelsInfo> GetDimensionChannelsInfo() override;
	virtual std::shared_ptr<libCZI::IDisplaySettings> GetDisplaySettings() const override;

private:
	void ParseDimensionInfo();

private:
	pugi::xml_node GetNode(const wchar_t* path) const;
	static pugi::xml_node GetNodeRelativeFromNode(pugi::xml_node node,const wchar_t* path);
};